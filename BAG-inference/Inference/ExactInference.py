# coding=gbk
#!/usr/bin/env python3
import copy
import itertools

import networkx as nx
import numpy as np
from tqdm import tqdm

from pgmpy.factors import factor_product
from pgmpy.inference import Inference
from EliminationOrder import (
    WeightedMinFill,
    MinNeighbors,
    MinFill,
    MinWeight,
)
from Models.BayesianModel import BayesianModel
from pgmpy.models import JunctionTree

class VariableElimination(Inference):
    def _get_working_factors(self, evidence):
        """
        Uses the evidence given to the query methods to modify the factors before running
        the variable elimination algorithm.

        Parameters
        ----------
        evidence: dict
            Dict of the form {variable: state}

        Returns
        -------
        dict: Modified working factors.
        """
        working_factors = {
            node: {factor for factor in self.factors[node]} for node in self.factors
        }

        # Dealing with evidence. Reducing factors over it before VE is run.
        if evidence:
            for evidence_var in evidence:
                for factor in working_factors[evidence_var]:
                    factor_reduced = factor.reduce(
                        [(evidence_var, evidence[evidence_var])], inplace=False
                    )
                    for var in factor_reduced.scope():
                        working_factors[var].remove(factor)
                        working_factors[var].add(factor_reduced)
                del working_factors[evidence_var]
        return working_factors

    def _get_elimination_order(
        self, variables, evidence, elimination_order, show_progress=True
    ):
        """
        Deals with all elimination order parameters given to _variable_elimination method
        and returns a list of variables that are to be eliminated

        Parameters
        ----------
        elimination_order: str or list

        Returns
        -------
        list: A list of variables names in the order they need to be eliminated.
        """
        to_eliminate = (
            set(self.variables)
            - set(variables)
            - set(evidence.keys() if evidence else [])
        )

        # Step 1: If elimination_order is a list, verify it's correct and return.
        if hasattr(elimination_order, "__iter__") and (
            not isinstance(elimination_order, str)
        ):
            if any(
                var in elimination_order
                for var in set(variables).union(
                    set(evidence.keys() if evidence else [])
                )
            ):
                raise ValueError(
                    "Elimination order contains variables which are in"
                    " variables or evidence args"
                )
            else:
                return elimination_order

        # Step 2: If elimination order is None or a Markov model, return a random order.
        elif (elimination_order is None) or (not isinstance(self.model, BayesianModel)):
            return to_eliminate

        # Step 3: If elimination order is a str, compute the order using the specified heuristic.
        elif isinstance(elimination_order, str) and isinstance(
            self.model, BayesianModel
        ):
            heuristic_dict = {
                "weightedminfill": WeightedMinFill,
                "minneighbors": MinNeighbors,
                "minweight": MinWeight,
                "minfill": MinFill,
            }
            elimination_order = heuristic_dict[elimination_order.lower()](
                self.model
            ).get_elimination_order(nodes=to_eliminate, show_progress=show_progress)
            return elimination_order

    def _variable_elimination(
        self,
        variables,
        operation,
        evidence=None,
        elimination_order="MinWeight",
        joint=True,
        show_progress=True,
    ):
        """
        Implementation of a generalized variable elimination.

        Parameters
        ----------
        variables: list, array-like
            variables that are not to be eliminated.

        operation: str ('marginalize' | 'maximize')
            The operation to do for eliminating the variable.

        evidence: dict
            a dict key, value pair as {var: state_of_var_observed}
            None if no evidence

        elimination_order: str or list (array-like)
            If str: Heuristic to use to find the elimination order.
            If array-like: The elimination order to use.
            If None: A random elimination order is used.
        """
        # Step 1: Deal with the input arguments.
        if isinstance(variables, str):
            raise TypeError("variables must be a list of strings")
        if isinstance(evidence, str):
            raise TypeError("evidence must be a list of strings")

        # Dealing with the case when variables is not provided.
        if not variables:
            all_factors = []
            for factor_li in self.factors.values():
                all_factors.extend(factor_li)
            if joint:
                return factor_product(*set(all_factors))
            else:
                return set(all_factors)

        # Step 2: Prepare data structures to run the algorithm.
        eliminated_variables = set()
        # Get working factors and elimination order
        working_factors = self._get_working_factors(evidence)
        elimination_order = self._get_elimination_order(
            variables, evidence, elimination_order, show_progress=show_progress
        )

        # Step 3: Run variable elimination
        if show_progress:
            pbar = tqdm(elimination_order)
        else:
            pbar = elimination_order

        #print('elimination order:',elimination_order)
        #print('pbar:',pbar)
        #print('working factors:',working_factors)

        for var in pbar:
            if show_progress:    # 按顺序删除，显示删除顺序最后一个
                pbar.set_description("Eliminating: {var}".format(var=var))
            # Removing all the factors containing the variables which are
            # eliminated (as all the factors should be considered only once)
            factors = [
                factor
                for factor in working_factors[var]
                if not set(factor.variables).intersection(eliminated_variables)
            ]
            #print('factors:::\n',factors)
            # ->[<DiscreteFactor representing phi(D:2, C:2) at 0x7ffd9c8cc110>, <DiscreteFactor representing phi(D:2, C:2, E:2) at 0x7ffd9c965f50>]

            phi = factor_product(*factors)
            #print('phi:\n',phi)
            phi = getattr(phi, operation)([var], inplace=False)   # 消去变量var
            #print('phi:\n',phi)
            #print('working_factors:::\n', working_factors)
            del working_factors[var]
            for variable in phi.variables:    # 删除var节点，并在phi相关节点加上phi信息
                working_factors[variable].add(phi)
            eliminated_variables.add(var)
            #print('working_factors:::\n',working_factors)

        # Step 4: Prepare variables to be returned.
        final_distribution = set()
        for node in working_factors:
            factors = working_factors[node]
            for factor in factors:
                if not set(factor.variables).intersection(eliminated_variables):
                    final_distribution.add(factor)

        if joint:
            if isinstance(self.model, BayesianModel):
                return factor_product(*final_distribution).normalize(inplace=False)
            else:
                return factor_product(*final_distribution)
        else:
            query_var_factor = {}
            for query_var in variables:
                phi = factor_product(*final_distribution)
                query_var_factor[query_var] = phi.marginalize(
                    list(set(variables) - set([query_var])), inplace=False
                ).normalize(inplace=False)
            return query_var_factor

    def query(
        self,
        variables,
        evidence=None,
        elimination_order="MinWeight",
        joint=True,
        show_progress=True,
    ):
        """
        Parameters
        ----------
        variables: list
            list of variables for which you want to compute the probability

        evidence: dict
            a dict key, value pair as {var: state_of_var_observed}
            None if no evidence

        elimination_order: list
            order of variable eliminations (if nothing is provided) order is
            computed automatically

        joint: boolean (default: True)
            If True, returns a Joint Distribution over `variables`.
            If False, returns a dict of distributions over each of the `variables`.

        Examples
        --------
        >>> from pgmpy.inference import VariableElimination
        >>> from pgmpy.models import BayesianModel
        >>> import numpy as np
        >>> import pandas as pd
        >>> values = pd.DataFrame(np.random.randint(low=0, high=2, size=(1000, 5)),
        ...                       columns=['A', 'B', 'C', 'D', 'E'])
        >>> model = BayesianModel([('A', 'B'), ('C', 'B'), ('C', 'D'), ('B', 'E')])
        >>> model.fit(values)
        >>> inference = VariableElimination(model)
        >>> phi_query = inference.query(['A', 'B'])
        """
        common_vars = set(evidence if evidence is not None else []).intersection(
            set(variables)
        )
        if common_vars:
            raise ValueError(
                f"Can't have the same variables in both `variables` and `evidence`. Found in both: {common_vars}"
            )

        return self._variable_elimination(
            variables=variables,
            operation="marginalize",
            evidence=evidence,
            elimination_order=elimination_order,
            joint=joint,
            show_progress=show_progress,
        )

    def max_marginal(
        self,
        variables=None,
        evidence=None,
        elimination_order="MinWeight",
        show_progress=True,
    ):
        """
        Computes the max-marginal over the variables given the evidence.

        Parameters
        ----------
        variables: list
            list of variables over which we want to compute the max-marginal.
        evidence: dict
            a dict key, value pair as {var: state_of_var_observed}
            None if no evidence
        elimination_order: list
            order of variable eliminations (if nothing is provided) order is
            computed automatically

        Examples
        --------
        >>> import numpy as np
        >>> import pandas as pd
        >>> from pgmpy.models import BayesianModel
        >>> from pgmpy.inference import VariableElimination
        >>> values = pd.DataFrame(np.random.randint(low=0, high=2, size=(1000, 5)),
        ...                       columns=['A', 'B', 'C', 'D', 'E'])
        >>> model = BayesianModel([('A', 'B'), ('C', 'B'), ('C', 'D'), ('B', 'E')])
        >>> model.fit(values)
        >>> inference = VariableElimination(model)
        >>> phi_query = inference.max_marginal(['A', 'B'])
        """
        if not variables:
            variables = []

        common_vars = set(evidence if evidence is not None else []).intersection(
            set(variables if variables is not None else [])
        )
        if common_vars:
            raise ValueError(
                f"Can't have the same variables in both `variables` and `evidence`. Found in both: {common_vars}"
            )

        final_distribution = self._variable_elimination(
            variables=variables,
            operation="maximize",
            evidence=evidence,
            elimination_order=elimination_order,
            show_progress=show_progress,
        )

        return np.max(final_distribution.values)

    def map_query(
        self,
        variables=None,
        evidence=None,
        elimination_order="MinWeight",
        show_progress=True,
    ):
        """
        Computes the MAP Query over the variables given the evidence.

        Note: When multiple variables are passed, it returns the map_query for each
        of them individually.

        Parameters
        ----------
        variables: list
            list of variables over which we want to compute the max-marginal.
        evidence: dict
            a dict key, value pair as {var: state_of_var_observed}
            None if no evidence
        elimination_order: list
            order of variable eliminations (if nothing is provided) order is
            computed automatically

        Examples
        --------
        >>> from pgmpy.inference import VariableElimination
        >>> from pgmpy.models import BayesianModel
        >>> import numpy as np
        >>> import pandas as pd
        >>> values = pd.DataFrame(np.random.randint(low=0, high=2, size=(1000, 5)),
        ...                       columns=['A', 'B', 'C', 'D', 'E'])
        >>> model = BayesianModel([('A', 'B'), ('C', 'B'), ('C', 'D'), ('B', 'E')])
        >>> model.fit(values)
        >>> inference = VariableElimination(model)
        >>> phi_query = inference.map_query(['A', 'B'])
        """
        common_vars = set(evidence if evidence is not None else []).intersection(
            set(variables if variables is not None else [])
        )
        if common_vars:
            raise ValueError(
                f"Can't have the same variables in both `variables` and `evidence`. Found in both: {common_vars}"
            )

        # TODO:Check the note in docstring. Change that behavior to return the joint MAP
        final_distribution = self._variable_elimination(
            variables=variables,
            operation="marginalize",
            evidence=evidence,
            elimination_order=elimination_order,
            joint=True,
            show_progress=show_progress,
        )
        argmax = np.argmax(final_distribution.values)
        assignment = final_distribution.assignment([argmax])[0]

        map_query_results = {}
        for var_assignment in assignment:
            var, value = var_assignment
            map_query_results[var] = value

        if not variables:
            return map_query_results
        else:
            return_dict = {}
            for var in variables:
                return_dict[var] = map_query_results[var]
            return return_dict

    def induced_graph(self, elimination_order):
        """
        Returns the induced graph formed by running Variable Elimination on the network.

        Parameters
        ----------
        elimination_order: list, array like
            List of variables in the order in which they are to be eliminated.

        Examples
        --------
        >>> import numpy as np
        >>> import pandas as pd
        >>> from pgmpy.models import BayesianModel
        >>> from pgmpy.inference import VariableElimination
        >>> values = pd.DataFrame(np.random.randint(low=0, high=2, size=(1000, 5)),
        ...                       columns=['A', 'B', 'C', 'D', 'E'])
        >>> model = BayesianModel([('A', 'B'), ('C', 'B'), ('C', 'D'), ('B', 'E')])
        >>> model.fit(values)
        >>> inference = VariableElimination(model)
        >>> inference.induced_graph(['C', 'D', 'A', 'B', 'E'])
        <networkx.classes.graph.Graph at 0x7f34ac8c5160>
        """
        # If the elimination order does not contain the same variables as the model
        if set(elimination_order) != set(self.variables):
            raise ValueError(
                "Set of variables in elimination order"
                " different from variables in model"
            )

        eliminated_variables = set()
        working_factors = {
            node: [factor.scope() for factor in self.factors[node]]
            for node in self.factors
        }

        # The set of cliques that should be in the induced graph
        cliques = set()
        for factors in working_factors.values():
            for factor in factors:
                cliques.add(tuple(factor))

        # Removing all the factors containing the variables which are
        # eliminated (as all the factors should be considered only once)
        for var in elimination_order:
            factors = [
                factor
                for factor in working_factors[var]
                if not set(factor).intersection(eliminated_variables)
            ]
            phi = set(itertools.chain(*factors)).difference({var})
            cliques.add(tuple(phi))
            del working_factors[var]
            for variable in phi:
                working_factors[variable].append(list(phi))
            eliminated_variables.add(var)

        edges_comb = [
            itertools.combinations(c, 2) for c in filter(lambda x: len(x) > 1, cliques)
        ]
        return nx.Graph(itertools.chain(*edges_comb))

    def induced_width(self, elimination_order):
        """
        Returns the width (integer) of the induced graph formed by running Variable Elimination on the network.
        The width is the defined as the number of nodes in the largest clique in the graph minus 1.

        Parameters
        ----------
        elimination_order: list, array like
            List of variables in the order in which they are to be eliminated.

        Examples
        --------
        >>> import numpy as np
        >>> import pandas as pd
        >>> from pgmpy.models import BayesianModel
        >>> from pgmpy.inference import VariableElimination
        >>> values = pd.DataFrame(np.random.randint(low=0, high=2, size=(1000, 5)),
        ...                       columns=['A', 'B', 'C', 'D', 'E'])
        >>> model = BayesianModel([('A', 'B'), ('C', 'B'), ('C', 'D'), ('B', 'E')])
        >>> model.fit(values)
        >>> inference = VariableElimination(model)
        >>> inference.induced_width(['C', 'D', 'A', 'B', 'E'])
        3
        """
        induced_graph = self.induced_graph(elimination_order)
        return nx.graph_clique_number(induced_graph) - 1


class BeliefPropagation(Inference):
    """
    Class for performing inference using Belief Propagation method.

    Creates a Junction Tree or Clique Tree (JunctionTree class) for the input
    probabilistic graphical model and performs calibration of the junction tree
    so formed using belief propagation.

    Parameters
    ----------
    model: BayesianModel, MarkovModel, FactorGraph, JunctionTree
        model for which inference is to performed
    """

    def __init__(self, model,order=None):
        super(BeliefPropagation, self).__init__(model)

        if not isinstance(model, JunctionTree):

            node_list=model.nodes
            if order=='random':   # 随机
                import random
                print('random')
                elimination_order=random.sample(node_list,len(node_list))
                self.junction_tree = model.to_junction_tree(order=elimination_order,heuristic=None)
            elif order in ['MinWeight','WeightedMinFill','MinNeighbors','MinFill']:

                from EliminationOrder import MinWeight,WeightedMinFill,MinNeighbors,MinFill
                elimination_model_options={'MinWeight':MinWeight,
                                   'WeightedMinFill':WeightedMinFill,
                                  'MinNeighbors':MinNeighbors,
                                  'MinFill':MinFill}

                elimination_order=elimination_model_options[order](model).get_elimination_order(node_list)
                #print(order+':')
                #print(elimination_order)
                #elimination_order = MinWeight(model).get_elimination_order(node_list)
                self.junction_tree = model.to_junction_tree(order=elimination_order,heuristic=None)
            elif order in ['H1','H2','H3','H4','H5','H6']:
                self.junction_tree = model.to_junction_tree(heuristic=order)
            elif order!=None and len(order)!=0:
                self.junction_tree=model.to_junction_tree(order=order,heuristic=None)
            else:
                self.junction_tree=model.to_junction_tree(heuristic='H1')

            # print(elimination_order)
            # print(elimination_order)
            #elimination_order=['A','B','C','D','E','F','G']
            #self.junction_tree = model.to_junction_tree(order=elimination_order)
        else:
            #print("It's ok.")
            self.junction_tree = copy.deepcopy(model)

        self.clique_beliefs = {}
        self.sepset_beliefs = {}

    def get_cliques(self):
        """
        Returns cliques used for belief propagation.
        """
        return self.junction_tree.nodes()

    def get_clique_beliefs(self):
        """
        Returns clique beliefs. Should be called after the clique tree (or
        junction tree) is calibrated.
        """
        return self.clique_beliefs

    def get_sepset_beliefs(self):
        """
        Returns sepset beliefs. Should be called after clique tree (or junction
        tree) is calibrated.
        """
        return self.sepset_beliefs

    def _update_beliefs(self, sending_clique, recieving_clique, operation):
        """
        This is belief-update method.

        Parameters
        ----------
        sending_clique: node (as the operation is on junction tree, node should be a tuple)
            Node sending the message
        recieving_clique: node (as the operation is on junction tree, node should be a tuple)
            Node recieving the message
        operation: str ('marginalize' | 'maximize')
            The operation to do for passing messages between nodes.

        Takes belief of one clique and uses it to update the belief of the
        neighboring ones.
        """

        '''
        sepset:  frozenset({'D', 'C'})
        sepset key:  frozenset({('D', 'C', 'E'), ('D', 'C', 'B', 'A')})
        sepset:  frozenset({'D', 'E'})
        sepset key:  frozenset({('D', 'F', 'E'), ('D', 'C', 'E')})
        sepset:  frozenset({'F'})
        sepset key:  frozenset({('D', 'F', 'E'), ('G', 'F')})
        '''
        #print('sending clique:',sending_clique)
        #print('receiving clique:',recieving_clique)
        sepset = frozenset(sending_clique).intersection(frozenset(recieving_clique))
        #print('sepset: ',sepset)
        sepset_key = frozenset((sending_clique, recieving_clique))
        #print('sepset key: ',sepset_key)

        # \sigma_{i \rightarrow j} = \sum_{C_i - S_{i, j}} \beta_i
        # marginalize the clique over the sepset
        sigma = getattr(self.clique_beliefs[sending_clique], operation)(
            list(frozenset(sending_clique) - sepset), inplace=False
        )

        self.clique_beliefs[recieving_clique] *= (
            sigma / self.sepset_beliefs[sepset_key]
            if self.sepset_beliefs[sepset_key]
            else sigma
        )

        #print('clique_beliefs[receiving_clique]:\n', self.clique_beliefs[recieving_clique])
        #print('sepset_beliefs[sepset_key]:\n', self.sepset_beliefs[sepset_key])

        # \mu_{i, j} = \sigma_{i \rightarrow j}
        self.sepset_beliefs[sepset_key] = sigma

    def _is_converged(self, operation):
        """
        Checks whether the calibration has converged or not. At convergence
        the sepset belief would be precisely the sepset marginal.

        Parameters
        ----------
        operation: str ('marginalize' | 'maximize')
            The operation to do for passing messages between nodes.
            if operation == marginalize, it checks whether the junction tree is calibrated or not
            else if operation == maximize, it checks whether the juction tree is max calibrated or not

        Formally, at convergence or at calibration this condition would be satisified for

        .. math:: \sum_{C_i - S_{i, j}} \beta_i = \sum_{C_j - S_{i, j}} \beta_j = \mu_{i, j}

        and at max calibration this condition would be satisfied

        .. math:: \max_{C_i - S_{i, j}} \beta_i = \max_{C_j - S_{i, j}} \beta_j = \mu_{i, j}
        """
        # If no clique belief, then the clique tree is not calibrated
        if not self.clique_beliefs:
            return False

        #print('junction tree edges:',self.junction_tree.edges)
        for edge in self.junction_tree.edges():
            sepset = frozenset(edge[0]).intersection(frozenset(edge[1]))
            sepset_key = frozenset(edge)
            if (
                edge[0] not in self.clique_beliefs
                or edge[1] not in self.clique_beliefs
                or sepset_key not in self.sepset_beliefs
            ):
                return False

            marginal_1 = getattr(self.clique_beliefs[edge[0]], operation)(
                list(frozenset(edge[0]) - sepset), inplace=False
            )
            marginal_2 = getattr(self.clique_beliefs[edge[1]], operation)(
                list(frozenset(edge[1]) - sepset), inplace=False
            )
            if (
                marginal_1 != marginal_2
                or marginal_1 != self.sepset_beliefs[sepset_key]
            ):
                return False
        return True

    def _calibrate_junction_tree(self, operation):
        """
        Generalized calibration of junction tree or clique using belief propagation. This method can be used for both
        calibrating as well as max-calibrating.
        Uses Lauritzen-Spiegelhalter algorithm or belief-update message passing.

        Parameters
        ----------
        operation: str ('marginalize' | 'maximize')
            The operation to do for passing messages between nodes.

        Reference
        ---------
        Algorithm 10.3 Calibration using belief propagation in clique tree
        Probabilistic Graphical Models: Principles and Techniques
        Daphne Koller and Nir Friedman.
        """
        # Initialize clique beliefs as well as sepset beliefs
        self.clique_beliefs = {
            clique: self.junction_tree.get_factors(clique)
            for clique in self.junction_tree.nodes()
        }
        self.sepset_beliefs = {
            frozenset(edge): None for edge in self.junction_tree.edges()
        }
        #print('clique beliefs: ',self.clique_beliefs)
        #print('sepset belief: ',self.sepset_beliefs)
        for clique in self.junction_tree.nodes():
            if not self._is_converged(operation=operation):
                neighbors = self.junction_tree.neighbors(clique)
                # print(clique,'clique neighbor->',list(neighbors))
                # update root's belief using nieighbor clique's beliefs
                # upward pass
                #print('=================================================')
                #print('neighbors:\n')
                #print(list(neighbors))
                for neighbor_clique in neighbors:
                    #print('neighbor:::',neighbor_clique)
                    self._update_beliefs(neighbor_clique, clique, operation=operation)
                bfs_edges = nx.algorithms.breadth_first_search.bfs_edges(
                    self.junction_tree, clique
                )

                # update the beliefs of all the nodes starting from the root to leaves using root's belief
                # downward pass
                for edge in bfs_edges:
                    #print('edges:',edge)
                    self._update_beliefs(edge[0], edge[1], operation=operation)
            else:
                break

    def calibrate(self):
        #print('**********')
        """
        Calibration using belief propagation in junction tree or clique tree.

        Examples
        --------
        >>> from pgmpy.models import BayesianModel
        >>> from pgmpy.factors.discrete import TabularCPD
        >>> from pgmpy.inference import BeliefPropagation
        >>> G = BayesianModel([('diff', 'grade'), ('intel', 'grade'),
        ...                    ('intel', 'SAT'), ('grade', 'letter')])
        >>> diff_cpd = TabularCPD('diff', 2, [[0.2], [0.8]])
        >>> intel_cpd = TabularCPD('intel', 3, [[0.5], [0.3], [0.2]])
        >>> grade_cpd = TabularCPD('grade', 3,
        ...                        [[0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        ...                         [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        ...                         [0.8, 0.8, 0.8, 0.8, 0.8, 0.8]],
        ...                        evidence=['diff', 'intel'],
        ...                        evidence_card=[2, 3])
        >>> sat_cpd = TabularCPD('SAT', 2,
        ...                      [[0.1, 0.2, 0.7],
        ...                       [0.9, 0.8, 0.3]],
        ...                      evidence=['intel'], evidence_card=[3])
        >>> letter_cpd = TabularCPD('letter', 2,
        ...                         [[0.1, 0.4, 0.8],
        ...                          [0.9, 0.6, 0.2]],
        ...                         evidence=['grade'], evidence_card=[3])
        >>> G.add_cpds(diff_cpd, intel_cpd, grade_cpd, sat_cpd, letter_cpd)
        >>> bp = BeliefPropagation(G)
        >>> bp.calibrate()
        """
        self._calibrate_junction_tree(operation="marginalize")

    def max_calibrate(self):
        """
        Max-calibration of the junction tree using belief propagation.

        Examples
        --------
        >>> from pgmpy.models import BayesianModel
        >>> from pgmpy.factors.discrete import TabularCPD
        >>> from pgmpy.inference import BeliefPropagation
        >>> G = BayesianModel([('diff', 'grade'), ('intel', 'grade'),
        ...                    ('intel', 'SAT'), ('grade', 'letter')])
        >>> diff_cpd = TabularCPD('diff', 2, [[0.2], [0.8]])
        >>> intel_cpd = TabularCPD('intel', 3, [[0.5], [0.3], [0.2]])
        >>> grade_cpd = TabularCPD('grade', 3,
        ...                        [[0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        ...                         [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        ...                         [0.8, 0.8, 0.8, 0.8, 0.8, 0.8]],
        ...                        evidence=['diff', 'intel'],
        ...                        evidence_card=[2, 3])
        >>> sat_cpd = TabularCPD('SAT', 2,
        ...                      [[0.1, 0.2, 0.7],
        ...                       [0.9, 0.8, 0.3]],
        ...                      evidence=['intel'], evidence_card=[3])
        >>> letter_cpd = TabularCPD('letter', 2,
        ...                         [[0.1, 0.4, 0.8],
        ...                          [0.9, 0.6, 0.2]],
        ...                         evidence=['grade'], evidence_card=[3])
        >>> G.add_cpds(diff_cpd, intel_cpd, grade_cpd, sat_cpd, letter_cpd)
        >>> bp = BeliefPropagation(G)
        >>> bp.max_calibrate()
        """
        self._calibrate_junction_tree(operation="maximize")

    def _query(
        self, variables, operation, evidence=None, joint=True, show_progress=True
    ):
        """
        This is a generalized query method that can be used for both query and map query.

        Parameters
        ----------
        variables: list
            list of variables for which you want to compute the probability
        operation: str ('marginalize' | 'maximize')
            The operation to do for passing messages between nodes.
        evidence: dict
            a dict key, value pair as {var: state_of_var_observed}
            None if no evidence

        Examples
        --------
        >>> from pgmpy.inference import BeliefPropagation
        >>> from pgmpy.models import BayesianModel
        >>> import numpy as np
        >>> import pandas as pd
        >>> values = pd.DataFrame(np.random.randint(low=0, high=2, size=(1000, 5)),
        ...                       columns=['A', 'B', 'C', 'D', 'E'])
        >>> model = BayesianModel([('A', 'B'), ('C', 'B'), ('C', 'D'), ('B', 'E')])
        >>> model.fit(values)
        >>> inference = BeliefPropagation(model)
        >>> phi_query = inference.query(['A', 'B'])

        References
        ----------
        Algorithm 10.4 Out-of-clique inference in clique tree
        Probabilistic Graphical Models: Principles and Techniques Daphne Koller and Nir Friedman.
        """

        is_calibrated = self._is_converged(operation=operation)
        # Calibrate the junction tree if not calibrated
        if not is_calibrated:
            self.calibrate()

        if not isinstance(variables, (list, tuple, set)):
            query_variables = [variables]
        else:
            query_variables = list(variables)
        query_variables.extend(evidence.keys() if evidence else [])
        #print('query_variables:',query_variables)

        # Find a tree T' such that query_variables are a subset of scope(T')
        nodes_with_query_variables = set()
        for var in query_variables:
            nodes_with_query_variables.update(
                filter(lambda x: var in x, self.junction_tree.nodes())
            )
        #print('nodes_with_query_variables:',nodes_with_query_variables)
        subtree_nodes = nodes_with_query_variables

        # Conversion of set to tuple just for indexing
        nodes_with_query_variables = tuple(nodes_with_query_variables)
        # As junction tree is a tree, that means that there would be only path between any two nodes in the tree
        # thus we can just take the path between any two nodes; no matter there order is
        for i in range(len(nodes_with_query_variables) - 1):
            subtree_nodes.update(
                nx.shortest_path(
                    self.junction_tree,
                    nodes_with_query_variables[i],
                    nodes_with_query_variables[i + 1],
                )
            )
        #print('subtree_nodes:',subtree_nodes)
        subtree_undirected_graph = self.junction_tree.subgraph(subtree_nodes)
        # Converting subtree into a junction tree
        if len(subtree_nodes) == 1:
            subtree = JunctionTree()
            subtree.add_node(subtree_nodes.pop())
        else:
            subtree = JunctionTree(subtree_undirected_graph.edges())

        # Selecting a node is root node. Root node would be having only one neighbor
        if len(subtree.nodes()) == 1:
            root_node = list(subtree.nodes())[0]
        else:
            root_node = tuple(
                filter(lambda x: len(list(subtree.neighbors(x))) == 1, subtree.nodes())
            )[0]
        clique_potential_list = [self.clique_beliefs[root_node]]
        # print('root node:',root_node)
        # print('clique potential:',clique_potential_list)

        # For other nodes in the subtree compute the clique potentials as follows
        # As all the nodes are nothing but tuples so simple set(root_node) won't work at it would update the set with'
        # all the elements of the tuple; instead use set([root_node]) as it would include only the tuple not the
        # internal elements within it.
        parent_nodes = set([root_node])
        nodes_traversed = set()
        while parent_nodes:
            parent_node = parent_nodes.pop()
            for child_node in set(subtree.neighbors(parent_node)) - nodes_traversed:
                clique_potential_list.append(
                    self.clique_beliefs[child_node]
                    / self.sepset_beliefs[frozenset([parent_node, child_node])]
                )
                parent_nodes.update([child_node])
                #print('parent nodes:',[parent_nodes])
                #print('clique_potential_list:',clique_potential_list)
            nodes_traversed.update([parent_node])
            #print('nodes_traversed:',nodes_traversed)

        # Add factors to the corresponding junction tree
        subtree.add_factors(*clique_potential_list)

        # Sum product variable elimination on the subtree
        variable_elimination = VariableElimination(subtree)
        if operation == "marginalize":
            return variable_elimination.query(
                variables=variables,
                evidence=evidence,
                joint=joint,
                show_progress=show_progress,
            )
        elif operation == "maximize":
            return variable_elimination.map_query(
                variables=variables,
                evidence=evidence,
                show_progress=show_progress
            )

    def query(self, variables, evidence=None, joint=True, show_progress=True):
        """
        Query method using belief propagation.

        Parameters
        ----------
        variables: list
            list of variables for which you want to compute the probability

        evidence: dict
            a dict key, value pair as {var: state_of_var_observed}
            None if no evidence

        joint: boolean
            If True, returns a Joint Distribution over `variables`.
            If False, returns a dict of distributions over each of the `variables`.

        Examples
        --------
        >>> from pgmpy.factors.discrete import TabularCPD
        >>> from pgmpy.models import BayesianModel
        >>> from pgmpy.inference import BeliefPropagation
        >>> bayesian_model = BayesianModel([('A', 'J'), ('R', 'J'), ('J', 'Q'),
        ...                                 ('J', 'L'), ('G', 'L')])
        >>> cpd_a = TabularCPD('A', 2, [[0.2], [0.8]])
        >>> cpd_r = TabularCPD('R', 2, [[0.4], [0.6]])
        >>> cpd_j = TabularCPD('J', 2,
        ...                    [[0.9, 0.6, 0.7, 0.1],
        ...                     [0.1, 0.4, 0.3, 0.9]],
        ...                    ['R', 'A'], [2, 2])
        >>> cpd_q = TabularCPD('Q', 2,
        ...                    [[0.9, 0.2],
        ...                     [0.1, 0.8]],
        ...                    ['J'], [2])
        >>> cpd_l = TabularCPD('L', 2,
        ...                    [[0.9, 0.45, 0.8, 0.1],
        ...                     [0.1, 0.55, 0.2, 0.9]],
        ...                    ['G', 'J'], [2, 2])
        >>> cpd_g = TabularCPD('G', 2, [[0.6], [0.4]])
        >>> bayesian_model.add_cpds(cpd_a, cpd_r, cpd_j, cpd_q, cpd_l, cpd_g)
        >>> belief_propagation = BeliefPropagation(bayesian_model)
        >>> belief_propagation.query(variables=['J', 'Q'],
        ...                          evidence={'A': 0, 'R': 0, 'G': 0, 'L': 1})
        """
        common_vars = set(evidence if evidence is not None else []).intersection(
            set(variables)
        )
        #print('common var:',common_vars)
        if common_vars:
            raise ValueError(
                f"Can't have the same variables in both `variables` and `evidence`. Found in both: {common_vars}"
            )

        return self._query(
            variables=variables,
            operation="marginalize",
            evidence=evidence,
            joint=joint,
            show_progress=show_progress,
        )

    def map_query(self, variables=None, evidence=None, show_progress=True):
        """
        MAP Query method using belief propagation.

        Note: When multiple variables are passed, it returns the map_query for each
        of them individually.

        Parameters
        ----------
        variables: list
            list of variables for which you want to compute the probability
        evidence: dict
            a dict key, value pair as {var: state_of_var_observed}
            None if no evidence

        Examples
        --------
        >>> from pgmpy.factors.discrete import TabularCPD
        >>> from pgmpy.models import BayesianModel
        >>> from pgmpy.inference import BeliefPropagation
        >>> bayesian_model = BayesianModel([('A', 'J'), ('R', 'J'), ('J', 'Q'),
        ...                                 ('J', 'L'), ('G', 'L')])
        >>> cpd_a = TabularCPD('A', 2, [[0.2], [0.8]])
        >>> cpd_r = TabularCPD('R', 2, [[0.4], [0.6]])
        >>> cpd_j = TabularCPD('J', 2,
        ...                    [[0.9, 0.6, 0.7, 0.1],
        ...                     [0.1, 0.4, 0.3, 0.9]],
        ...                    ['R', 'A'], [2, 2])
        >>> cpd_q = TabularCPD('Q', 2,
        ...                    [[0.9, 0.2],
        ...                     [0.1, 0.8]],
        ...                    ['J'], [2])
        >>> cpd_l = TabularCPD('L', 2,
        ...                    [[0.9, 0.45, 0.8, 0.1],
        ...                     [0.1, 0.55, 0.2, 0.9]],
        ...                    ['G', 'J'], [2, 2])
        >>> cpd_g = TabularCPD('G', 2, [[0.6], [0.4]])
        >>> bayesian_model.add_cpds(cpd_a, cpd_r, cpd_j, cpd_q, cpd_l, cpd_g)
        >>> belief_propagation = BeliefPropagation(bayesian_model)
        >>> belief_propagation.map_query(variables=['J', 'Q'],
        ...                              evidence={'A': 0, 'R': 0, 'G': 0, 'L': 1})
        """
        common_vars = set(evidence if evidence is not None else []).intersection(
            set(variables if variables is not None else [])
        )
        if common_vars:
            raise ValueError(
                f"Can't have the same variables in both `variables` and `evidence`. Found in both: {common_vars}"
            )

        # TODO:Check the note in docstring. Change that behavior to return the joint MAP
        if not variables:
            variables = set(self.variables)

        final_distribution = self._query(
            variables=variables,
            operation="marginalize",
            evidence=evidence,
            show_progress=show_progress,
        )

        # To handle the case when no argument is passed then
        # _variable_elimination returns a dict.
        argmax = np.argmax(final_distribution.values)
        assignment = final_distribution.assignment([argmax])[0]

        map_query_results = {}
        for var_assignment in assignment:
            var, value = var_assignment
            map_query_results[var] = value

        if not variables:
            return map_query_results
        else:
            return_dict = {}
            for var in variables:
                return_dict[var] = map_query_results[var]
            return return_dict
