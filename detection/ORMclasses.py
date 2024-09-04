import os
import numpy as np 
import pandas as pd 
import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String, DateTime
import datetime as dt

'''
Declaring the ORM class here
'''
Base = declarative_base()

class Property(Base):
    
    __tablename__ = 'SysClient0358Properties'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    property_id =  Column(String(128))
    acuity_level = Column(String(1))
    base_address = Column(String(128))
    command_line = Column(String(1024))
    context_info = Column(String(1024))
    data = Column(String(128))
    dest_ip = Column(String(32))
    dest_port = Column(Integer)
    direction = Column(Integer)            
    end_time = Column(DateTime)
    file_path = Column(String(256))
    image_path = Column(String(256))
    info_class = Column(String(128))
    key = Column(String(256))
    l4protocol = Column(Integer)
    logon_id = Column(String(64))
    module_path = Column(String(256))
    name =  Column(String(128))
    new_path = Column(String(256))
    parent_image_path = Column(String(256))
    path = Column(String(256))
    payload = Column(String(128))
    pid = Column(Integer)
    ppid = Column(Integer)
    priveleges = Column(String(128))
    requesting_domain = Column(String(128))
    requesting_logon_id = Column(String(128))
    requesting_user = Column(String(128))
    service_type = Column(String(128))
    sid = Column(String(64))
    size= Column(Integer) 
    src_ip = Column(String(32))
    src_pid = Column(Integer)
    src_port = Column(Integer)
    src_tid = Column(Integer)
    stack_base = Column(String(128))
    stack_limit = Column(String(128))
    start_address = Column(String(128))
    start_time = Column(DateTime)
    start_type = Column(String(128))
    subprocess_tag = Column(String(128))
    task_name = Column(String(128))
    task_pid = Column(Integer)
    task_process_uuid = Column(String(128))
    tgt_pid = Column(Integer)
    tgt_pid_uuid = Column(String(128))
    tgt_tid = Column(Integer)
    tid = Column(String(64))
    type = Column(String(128))
    user = Column(String(128))
    user_name = Column(String(128))
    user_stack_base = Column(String(128))
    user_stack_limit = Column(String(128))
    value = Column(String(128))
    
    def __init__(self, p_id = None,  acuity_level = 0 , base_address = None, command_line = None, 
                context_info = None , data = None, dest_ip = None, dest_port = None, direction = None , end_time = None,
                file_path= None, image_path = None, info_class = None , key= None,  l4protocol = None,
                logon_id = None, module_path = None, name = None, new_path = None,
                parent_image_path = None, path = None, payload = None, pid = None, ppid = None, privileges = None, 
                requesting_domain = None, requesting_logon_id = None, requesting_user = None,
                service_type = None, sid = None, size = None, src_ip = None, src_pid = None, src_port = None,
                src_tid = None, stack_base = None, stack_limit = None , start_address = None, start_time = None, 
                start_type = None, subprocess_tag = None, task_name = None, task_pid = None,
                task_process_uuid = None, tgt_pid = None, tgt_pid_uuid = None, tgt_tid = None, tid = None,
                type = None, user = None, user_name = None, user_stack_base = None, user_stack_limit = None, value = None):
        
        self.property_id = p_id
        self.acuity_level = acuity_level
        self.base_address = base_address
        self.command_line = command_line
        self.context_info = context_info
        self.data = data
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        
        if direction != None and direction == 'inbound':
            self.direction = 0
        elif direction != None and direction == 'outbound':
            self.direction = 1
        else:
            self.direction = -1
            
        if end_time != None:
            self.end_time = dt.datetime.fromisoformat(end_time) # Please note this or be prepared to have all inds of errors thrown at you
        else:
            self.end_time = None
        
        self.file_path = file_path
        self.image_path = image_path
        self.info_class = info_class
        self.key = key
        self.l4protocol = l4protocol
        self.logon_id = logon_id
        self.module_path = module_path
        self.name =  name
        self.new_path = new_path
        self.parent_image_path = parent_image_path
        self.path = path
        self.payload = payload
        self.pid = pid
        self.ppid = ppid
        self.privileges = privileges
        self.requesting_domain = requesting_domain
        self.requesting_logon_id = requesting_logon_id
        self.requesting_user = requesting_user
        self.service_type = service_type
        self.sid = sid
        self.size= size 
        self.src_ip = src_ip
        self.src_pid = src_pid
        self.src_port = src_port
        self.src_tid = src_tid
        self.stack_base = stack_base
        self.stack_limit = stack_limit
        self.start_address = start_address
        
        if start_time != None:
            self.start_time = dt.datetime.fromisoformat(start_time) # Please look above for the previous comment if you do not want to tear your hair in agony
        else:
            self.start_time = None
        
        self.start_type = start_type
        self.subprocess_tag = subprocess_tag
        self.task_name = task_name
        self.task_pid = task_pid
        self.task_process_uuid = task_process_uuid 
        self.tgt_pid = tgt_pid
        self.tgt_pid_uuid = tgt_pid_uuid
        self.tgt_tid = tgt_tid
        self.tid = tid
        self.type = type
        self.user = user
        self.user_name = user_name
        self.user_stack_base = user_stack_base
        self.user_stack_limit = user_stack_limit
        self.value = value

'''
This is the Event ORM class. In case of graph building, the actorID and the objectID will be the major players.
We need to find a way to encode the other fields though. I am not sure yet how to accomplish this.
'''

class Event(Base):
    __tablename__ = 'SysClient0358Events'
    __table_args__ = {'extend_existing': True} 
    
    id = Column(Integer, primary_key = True )
    
    event_id = Column(String(128))
    object = Column(String(32))
    objectID= Column(String(64))
    action = Column(String(32))
    actorID = Column(String(64))
    hostname = Column(String(128))
    pid = Column(Integer)
    ppid = Column(Integer)
    principal = Column(String(256))
    tid = Column(Integer)
    timestamp = Column(DateTime)
    
    def __init__(self, e_id = None ,object = None, objectID= None, action= None, actorID= None, hostname= None, 
                pid= 0, ppid= 0, principal= None, tid = 0, timestamp = None):
        self.event_id = e_id
        self.object = object
        self.objectID= objectID
        self.action = action
        self.actorID = actorID
        self.hostname = hostname
        self.pid = pid
        self.ppid = ppid
        self.principal = principal
        self.tid = tid
        if timestamp != None:
            self.timestamp = dt.datetime.fromisoformat(timestamp) # Do I need to comment again???????????
        else:
            self.timestamp = None
        
    def __str__(self):
        return "Event Id: {0}, Event Type: {1},{2}, Event Time: {3}, Event Actor: {4}".format(self.id, self.object, self.action, self.timestamp, self.actorID)

def custom_date_time_formatter(param_date_string):
    iso_date_time_string = param_date_string[0:-6]
    try:
        return dt.datetime.strptime(iso_date_time_string,'%Y-%m-%dT%H:%M:%S.%f')
    except:
        if len(iso_date_time_string) <= 19:
            return dt.datetime.strptime(iso_date_time_string,'%Y-%m-%dT%H:%M:%S')

def get_event(json_event):
    '''
    As the name suggests, the function will take a json object as parameter and will return the corresponding event object which will later be used to be pushed in the database.
    '''
    event = Event()
    fields = json_event.keys()
    for field in fields:
        if isinstance(json_event[field], dict): # 检查json_event[field]是否是字典
            pass
        elif field == 'id':
            setattr(event, 'event_id', json_event[field])
        elif field == 'timestamp':
            setattr(event, 'timestamp', custom_date_time_formatter(json_event[field]))
        else:
            setattr(event, field, json_event[field])
    return event

def get_property( event_id, json_property):
    '''
    It will take the json property object as input and will return the corresponding python property object as output which will be dumped in the db.
    In order to map the property with a specific event it will also take event_id as input.
    '''
    
    
    property = Property()
    fields = json_property.keys()
    property.property_id = event_id
    for field in fields:
        if isinstance(json_property[field], dict): # This is something I am not sure about. For the sake of error-handling I am putting it here now
            pass
        
        elif field == 'direction':
            if json_property['direction'] == 'inbound':
                setattr(property, field, 0)
            elif json_property['direction'] == 'outbound':
                setattr(property, field, 1)
            else:
                setattr(property, field, -1)
        
        elif field == 'end_time':
            try:
                setattr(property, field, dt.datetime.fromtimestamp(int(json_property[field])))
            except:
                print("End time exception encountered for id {}, for value: {}".format(event_id, json_property[field]))
                setattr(property, field, dt.datetime.now())
                        
        
        elif field == 'start_time':
            try:
                setattr(property, field, dt.datetime.fromtimestamp(int(json_property[field])))
            except:
                setattr(property, field, dt.datetime.now())
        else:
            setattr(property, field, json_property[field])
    return property

def property_validator(property_obj):
    '''
        Takes a property object and checks the fields before dumping into db.
        P.S. This is a boierplate code. You can improve it by creating a dictionary that contains 
        mapping between field name and limit value then iterate over it. But I was in a time crunch.
    '''
    
    if property_obj.base_address != None and len(property_obj.base_address)>128:
        property_obj.base_address = property_obj.base_address[-127:]
    if property_obj.command_line != None and len(property_obj.command_line)>1024:
        property_obj.command_line = property_obj.command_line[-1023:]
    if property_obj.context_info != None and len(property_obj.context_info)>1024:
        property_obj.context_info = property_obj.context_info[-1023:]
    if property_obj.data != None and len(property_obj.data)>128:
        property_obj.data = property_obj.data[-127:]    
    if property_obj.file_path != None and len(property_obj.file_path)>256:
        property_obj.file_path = property_obj.file_path[-255:]
    if property_obj.image_path != None and len(property_obj.image_path)>256:
        property_obj.image_path = property_obj.image_path[-255:]
    if property_obj.info_class != None and len(property_obj.info_class)>128:
        property_obj.info_class = property_obj.info_class[-127:]    
    if property_obj.key != None and len(property_obj.key)>256:
        property_obj.key = property_obj.key[-255:]
    if property_obj.logon_id != None and len(property_obj.logon_id)>64:
        property_obj.logon_id = property_obj.logon_id[-63:]
    if property_obj.module_path != None and len(property_obj.module_path)>256:
        property_obj.module_path = property_obj.context_info[-255:]
    if property_obj.name != None and len(property_obj.name)>128:
        property_obj.name = property_obj.name[-127:]
    if property_obj.new_path != None and len(property_obj.new_path)>256:
        property_obj.new_path = property_obj.new_path[-255:]
    if property_obj.parent_image_path != None and len(property_obj.parent_image_path)>256:
        property_obj.parent_image_path = property_obj.parent_image_path[-255:]
    if property_obj.path != None and len(property_obj.path)>256:
        property_obj.path = property_obj.path[-255:]
    if property_obj.payload != None and len(property_obj.payload)>128:
        property_obj.payload = property_obj.payload[-127:]
    if property_obj.priveleges != None and len(property_obj.priveleges)>128:
        property_obj.priveleges = property_obj.priveleges[-127:]
    if property_obj.requesting_domain != None and len(property_obj.requesting_domain)>128:
        property_obj.requesting_domain = property_obj.requesting_domain[-127:]
    if property_obj.requesting_logon_id != None and len(property_obj.requesting_logon_id)>128:
        property_obj.requesting_logon_id = property_obj.requesting_logon_id[-127:]
    if property_obj.requesting_user != None and len(property_obj.requesting_user)>128:
        property_obj.requesting_user = property_obj.requesting_user[-127:]
    if property_obj.service_type != None and len(property_obj.service_type)>128:
        property_obj.service_type = property_obj.service_type[-127:]
    if property_obj.sid != None and len(property_obj.sid)>64:
        property_obj.sid = property_obj.sid[-63:]
    if property_obj.stack_base != None and len(property_obj.stack_base)>128:
        property_obj.stack_base = property_obj.stack_base[-127:]
    if property_obj.stack_limit != None and len(property_obj.stack_limit)>128:
        property_obj.stack_limit = property_obj.stack_limit[-127:]
    if property_obj.start_address != None and len(property_obj.start_address)>128:
        property_obj.start_address = property_obj.start_address[-127:]
    if property_obj.start_type != None and len(property_obj.start_type)>128:
        property_obj.start_type = property_obj.start_type[-127:]
    if property_obj.subprocess_tag != None and len(property_obj.subprocess_tag)>128:
        property_obj.subprocess_tag = property_obj.subprocess_tag[-127:]
    if property_obj.task_name != None and len(property_obj.task_name)>128:
        property_obj.task_name = property_obj.task_name[-127:]
    if property_obj.task_process_uuid != None and len(property_obj.task_process_uuid)>128:
        property_obj.task_process_uuid = property_obj.task_process_uuid[-127:]
    if property_obj.tid != None and len(property_obj.tid)>64:
        property_obj.tid = property_obj.tid[-63:]
    if property_obj.type != None and len(property_obj.type)>128:
        property_obj.type = property_obj.type[-127:]
    if property_obj.user != None and len(property_obj.user)>128:
        property_obj.user = property_obj.user[-127:]
    if property_obj.user_name != None and len(property_obj.user_name)>128:
        property_obj.user_name = property_obj.user_name[-127:]    
    if property_obj.user_stack_base != None and len(property_obj.user_stack_base)>128:
        property_obj.user_stack_base = property_obj.user_stack_base[-127:]
    if property_obj.user_stack_limit != None and len(property_obj.user_stack_limit)>128:
        property_obj.user_stack_limit = property_obj.user_stack_limit[-127:]
    if property_obj.value != None and len(property_obj.value)>128:
        property_obj.value = property_obj.value[-127:]
