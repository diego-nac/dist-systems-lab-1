# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: device.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='device.proto',
  package='device',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0c\x64\x65vice.proto\x12\x06\x64\x65vice\"\x99\x01\n\x0f\x44\x65viceDiscovery\x12\x11\n\tdevice_id\x18\x01 \x01(\t\x12\x11\n\tdevice_ip\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65vice_port\x18\x03 \x01(\x05\x12\x13\n\x0b\x64\x65vice_type\x18\x04 \x01(\t\x12\r\n\x05state\x18\x05 \x01(\t\x12\x12\n\nluminosity\x18\x06 \x01(\x05\x12\x13\n\x0btemperature\x18\x07 \x01(\x02\"G\n\rDeviceCommand\x12\x11\n\tdevice_id\x18\x01 \x01(\t\x12\x0f\n\x07\x63ommand\x18\x02 \x01(\t\x12\x12\n\nluminosity\x18\x03 \x01(\x05\"3\n\x0f\x43ommandResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"6\n\nDeviceList\x12(\n\x07\x64\x65vices\x18\x01 \x03(\x0b\x32\x17.device.DeviceDiscovery\"\x07\n\x05\x45mptyb\x06proto3')
)




_DEVICEDISCOVERY = _descriptor.Descriptor(
  name='DeviceDiscovery',
  full_name='device.DeviceDiscovery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='device_id', full_name='device.DeviceDiscovery.device_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='device_ip', full_name='device.DeviceDiscovery.device_ip', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='device_port', full_name='device.DeviceDiscovery.device_port', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='device_type', full_name='device.DeviceDiscovery.device_type', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='state', full_name='device.DeviceDiscovery.state', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='luminosity', full_name='device.DeviceDiscovery.luminosity', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='temperature', full_name='device.DeviceDiscovery.temperature', index=6,
      number=7, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=25,
  serialized_end=178,
)


_DEVICECOMMAND = _descriptor.Descriptor(
  name='DeviceCommand',
  full_name='device.DeviceCommand',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='device_id', full_name='device.DeviceCommand.device_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='command', full_name='device.DeviceCommand.command', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='luminosity', full_name='device.DeviceCommand.luminosity', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=180,
  serialized_end=251,
)


_COMMANDRESPONSE = _descriptor.Descriptor(
  name='CommandResponse',
  full_name='device.CommandResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='device.CommandResponse.success', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='message', full_name='device.CommandResponse.message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=253,
  serialized_end=304,
)


_DEVICELIST = _descriptor.Descriptor(
  name='DeviceList',
  full_name='device.DeviceList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='devices', full_name='device.DeviceList.devices', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=306,
  serialized_end=360,
)


_EMPTY = _descriptor.Descriptor(
  name='Empty',
  full_name='device.Empty',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=362,
  serialized_end=369,
)

_DEVICELIST.fields_by_name['devices'].message_type = _DEVICEDISCOVERY
DESCRIPTOR.message_types_by_name['DeviceDiscovery'] = _DEVICEDISCOVERY
DESCRIPTOR.message_types_by_name['DeviceCommand'] = _DEVICECOMMAND
DESCRIPTOR.message_types_by_name['CommandResponse'] = _COMMANDRESPONSE
DESCRIPTOR.message_types_by_name['DeviceList'] = _DEVICELIST
DESCRIPTOR.message_types_by_name['Empty'] = _EMPTY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DeviceDiscovery = _reflection.GeneratedProtocolMessageType('DeviceDiscovery', (_message.Message,), dict(
  DESCRIPTOR = _DEVICEDISCOVERY,
  __module__ = 'device_pb2'
  # @@protoc_insertion_point(class_scope:device.DeviceDiscovery)
  ))
_sym_db.RegisterMessage(DeviceDiscovery)

DeviceCommand = _reflection.GeneratedProtocolMessageType('DeviceCommand', (_message.Message,), dict(
  DESCRIPTOR = _DEVICECOMMAND,
  __module__ = 'device_pb2'
  # @@protoc_insertion_point(class_scope:device.DeviceCommand)
  ))
_sym_db.RegisterMessage(DeviceCommand)

CommandResponse = _reflection.GeneratedProtocolMessageType('CommandResponse', (_message.Message,), dict(
  DESCRIPTOR = _COMMANDRESPONSE,
  __module__ = 'device_pb2'
  # @@protoc_insertion_point(class_scope:device.CommandResponse)
  ))
_sym_db.RegisterMessage(CommandResponse)

DeviceList = _reflection.GeneratedProtocolMessageType('DeviceList', (_message.Message,), dict(
  DESCRIPTOR = _DEVICELIST,
  __module__ = 'device_pb2'
  # @@protoc_insertion_point(class_scope:device.DeviceList)
  ))
_sym_db.RegisterMessage(DeviceList)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), dict(
  DESCRIPTOR = _EMPTY,
  __module__ = 'device_pb2'
  # @@protoc_insertion_point(class_scope:device.Empty)
  ))
_sym_db.RegisterMessage(Empty)


# @@protoc_insertion_point(module_scope)
