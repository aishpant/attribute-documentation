@r exists@
identifier t, name, convert_type;
expression list es;
@@

 show_fn (...)
 {
  ...
  struct t *name = convert_type(...);
  ...
* sprintf(es)
  ...
 }

@script:python@
struct_type << r.t;
@@

print ('struct_type ' + struct_type)

