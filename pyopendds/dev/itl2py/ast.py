from pathlib import Path
from enum import Enum, auto

class Name:

  def __init__(self, itl_name=None, parts=None):
    if itl_name is not None and parts is None:
      self.itl_name = itl_name
      self.parts = itl_name.split(':')[1].split('/')
    elif itl_name is None and parts is not None:
      self.itl_name = 'IDL:{}:1.0'.format('/'.join(parts))
      self.parts = parts
    else:
      raise ValueError('Either parts or itl_name must be passed')

  def join(self,sep = '.'):
    return sep.join(self.parts)

class Node:

  def __init__(self, note):
    self.note = note
    self.name = None
    self.is_topic_type = False

  def set_name(self, itl_name=None, parts=None):
    self.name = Name(itl_name=itl_name, parts=parts)

  def local_name(self):
    if self.name:
      return self.name.parts[-1]
    return None

  def parent_name(self):
    if self.name:
      return Name(parts=self.name.parts[:-1])
    return None

  def accept(self, visitor):
    raise NotImplementedError

class Module(Node):

  def __init__(self, parent, name):
    super().__init__(None)
    self.parent = parent
    name_parts = []
    if parent and name:
      name_parts.extend(parent.name.parts)
      name_parts.append(name)
    self.set_name(parts=name_parts)
    self.submodules = {}
    self.types = {}

  def accept(self, visitor):
    for type_node in self.types.values():
      type_node.accept(visitor)

    for submodule in self.submodules.values():
      visitor.visit_module(submodule)

class PrimitiveType(Node):

  class Kind(Enum):
    u8 = auto()
    i8 = auto()
    u16 = auto()
    i16 = auto()
    u32 = auto()
    i32 = auto()
    u64 = auto()
    i64 = auto()
    f32 = auto()
    f64 = auto()
    c8 = auto()
    s8 = auto()

  def __init__(self, kind, note):
    super().__init__(note)
    if kind not in self.Kind:
      raise ValueError('Invalid Primitive Kind: ' + repr(kind))
    self.kind = kind

  def is_int(self):
    return {
      self.Kind.u8: True,
      self.Kind.i8: True,
      self.Kind.u16: True,
      self.Kind.i16: True,
      self.Kind.u32: True,
      self.Kind.i32: True,
      self.Kind.u64: True,
      self.Kind.i64: True,
      self.Kind.f32: False,
      self.Kind.f64: False,
      self.Kind.c8: False,
      self.Kind.s8: False,
    }[self.kind]

  def is_string(self):
    return {
      self.Kind.u8: False,
      self.Kind.i8: False,
      self.Kind.u16: False,
      self.Kind.i16: False,
      self.Kind.u32: False,
      self.Kind.i32: False,
      self.Kind.u64: False,
      self.Kind.i64: False,
      self.Kind.f32: False,
      self.Kind.f64: False,
      self.Kind.c8: False,
      self.Kind.s8: True,
    }[self.kind]

class StructType(Node):

  def __init__(self, note):
    super().__init__(note)
    self.fields = {}

  def add_field(self, name, type_node, optional):
    self.fields[name] = (type_node, optional)

  def accept(self, visitor):
    visitor.visit_struct(self)

class EnumType(Node):

  def __init__(self, note):
    super().__init__(note)
    self.members = {}
    self.default_member = None

  def add_member(self, name, value):
    self.members[name] = value
    if self.default_member is None:
      self.default_member = name

  def accept(self, visitor):
    visitor.visit_enum(self)

class NodeVisitor:

  def visit_module(self, module):
    module.accept(self)

  def visit_struct(self, struct_type):
    raise NotImplementedError

  def visit_enum(self, enum_type):
    raise NotImplementedError

class Output(NodeVisitor):

  def __init__(self, path):
    self.path = Path(path)
    self.contents = []

  def before(self):
    return ''

  def after(self):
    return ''

  def write(self):
    self.path.write_text(self.before() + ''.join(self.contents) + self.after())

  def append(self, what):
    self.contents.append(what + '\n')

def get_ast(types):
  root_module = Module(None, '')
  for type_node in types.values():
    module = root_module
    for module_name in type_node.parent_name().parts:
      if module_name not in module.submodules:
        module.submodules[module_name] = Module(module, module_name)
      module = module.submodules[module_name]
    module.types[type_node.name.itl_name] = type_node
  return root_module