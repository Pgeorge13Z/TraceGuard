import os
import json
import ORMclasses as ORM
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def read_from_compressed_json(filename, hostname ,linecount = None):
    """Reads the line by line from the files. In the file each line is JSON formatted.
    Returns a list of "Object of Interest" and corresponding "Properties of Interest".

    Args:
        filename ([String]): [Absolute File Path of the json file.]
        linecount ([Integer], optional): [Read specified number of lines from the file.]. Defaults to None.
    """
    line_read_count = 0
    
    file_obj = 0
    process_obj = 0
    shell_cmd_obj = 0
    flow_msg_obj = 0

    non_host_line_count = 0

    obj_holder = []
    property_holder = []
    stats = dict()
    with open(filename) as json_event_file:
        for json_event in json_event_file:
            obj = json.loads(json_event)
            line_read_count += 1
            if obj['hostname'] == hostname:
                if obj['object'] == 'FILE':
                    obj_holder.append(ORM.get_event(obj))
                    properties_of_the_event = ORM.get_property(obj['id'], obj['properties'])
                    ORM.property_validator(properties_of_the_event)
                    property_holder.append(properties_of_the_event)
                    file_obj += 1
                elif obj['object'] == 'PROCESS':
                    obj_holder.append(ORM.get_event(obj))
                    properties_of_the_event = ORM.get_property(obj['id'], obj['properties'])
                    ORM.property_validator(properties_of_the_event)
                    property_holder.append(properties_of_the_event)
                    process_obj += 1
                elif obj['object'] == 'SHELL':
                    obj_holder.append(ORM.get_event(obj))
                    properties_of_the_event = ORM.get_property(obj['id'], obj['properties'])
                    ORM.property_validator(properties_of_the_event)
                    property_holder.append(properties_of_the_event)
                    shell_cmd_obj += 1 
                elif obj['object'] == 'FLOW' and obj['action'] ==  'MESSAGE':
                    obj_holder.append(ORM.get_event(obj))
                    properties_of_the_event = ORM.get_property(obj['id'], obj['properties'])
                    ORM.property_validator(properties_of_the_event)
                    property_holder.append(properties_of_the_event)
                    flow_msg_obj += 1
            else:
                non_host_line_count+=1
            
            if line_read_count == linecount:
                break
            if line_read_count%1000000 == 0:
                stats['file'] = file_obj
                stats['process'] = process_obj
                stats['shell'] = shell_cmd_obj
                stats['flow'] = flow_msg_obj
                print("Current line read count: {}".format(line_read_count))
                print(stats, flush=True)

    
    
    print("non host line count:{} total line count: {}".format(non_host_line_count, line_read_count))
    return obj_holder, property_holder, stats

def bulk_dump_in_db(events, properties, connection_string, batch_size = 100000):
    """[This function takes the objects and properties and then dumps them in the database tables.]

    Args:
        events ([list]): [List of ORM.Event to be pushed in the db]
        properties ([list]): [List of ORM.property to be pushed in the db]
        connection_string ([String]): [postgresql connection string formatted to be compatible with pyscopg2]
        batch_size ([Integer]): [determines how many rows are dumped in db in one commit] Defaults to 100000
    """

    psql_engine = create_engine(connection_string)
    ORM.Base.metadata.create_all(psql_engine)
    Session = sessionmaker(bind=psql_engine)
    session = Session()

    start_idx = 0
    end_idx = batch_size
    dump_count = 0
    while end_idx < len(events) :

        session.bulk_save_objects(events[start_idx:end_idx])
        session.bulk_save_objects(properties[start_idx:end_idx])
        session.commit()
        start_idx = end_idx
        end_idx += batch_size
        print("Dump Iteration Complete {}".format(dump_count))
        dump_count += 1

    end_idx = len(events)
    
    if start_idx < end_idx:
        session.bulk_save_objects(events[start_idx:end_idx])
        session.bulk_save_objects(properties[start_idx:end_idx])
        session.commit()
    
    
    session.close()
    




if __name__=="__main__":
    psql_conn_string = 'postgresql+psycopg2://csephase2:csephase@@localhost/csephase2'
    if len(sys.argv) < 3:
        print("The correct format is <scriptname> <filename> <hostname> <optional:linecount>")
    elif len(sys.argv) == 3:
        objects, properties, op_stats = read_from_compressed_json(sys.argv[1], sys.argv[2])
        print(op_stats, len(objects), len(properties))
        bulk_dump_in_db(objects, properties, psql_conn_string)
    elif len(sys.argv) == 4:
        objects, properties, op_stats = read_from_compressed_json(sys.argv[1], sys.argv[2], int(sys.argv[3]))
        print(op_stats, len(objects), len(properties))
        bulk_dump_in_db(objects, properties, psql_conn_string)
    else:
        print("Extra parameter encountered. Please check the command and again in this format: <scriptname> <filename> <hostname> <optional:linecount>")

    

    

