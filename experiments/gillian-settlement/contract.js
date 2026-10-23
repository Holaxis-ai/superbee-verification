/**
 @id settleAgainstIntent
 @pre (outcome == #o) * (intent == #i) * JSObject(#o) * DataProp(#o, "kind", "conflict") * DataProp(#o, "actual", #v) * JSObject(#i) * DataProp(#i, "local", #v) * types(#v: Str) * GlobalObject() * ObjectPrototype($lobj_proto)
 @post JSObject(#o) * DataProp(#o, "kind", "conflict") * DataProp(#o, "actual", #v) * JSObject(#i) * DataProp(#i, "local", #v) * types(#v: Str) * GlobalObject() * ObjectPrototype($lobj_proto) * JSObject(ret) * DataProp(ret, "kind", "committed") * DataProp(ret, "version", #v)

 @pre (outcome == #o) * (intent == #i) * JSObject(#o) * DataProp(#o, "kind", "conflict") * DataProp(#o, "actual", #a) * JSObject(#i) * DataProp(#i, "local", #v) * types(#a: Str, #v: Str) * (! (#a == #v)) * GlobalObject() * ObjectPrototype($lobj_proto)
 @post JSObject(#o) * DataProp(#o, "kind", "conflict") * DataProp(#o, "actual", #a) * JSObject(#i) * DataProp(#i, "local", #v) * types(#a: Str, #v: Str) * (! (#a == #v)) * GlobalObject() * ObjectPrototype($lobj_proto) * (ret == #o)

 @pre (outcome == #o) * (intent == #i) * JSObject(#o) * DataProp(#o, "kind", "conflict") * DataProp(#o, "actual", null) * JSObject(#i) * DataProp(#i, "local", #v) * types(#v: Str) * GlobalObject() * ObjectPrototype($lobj_proto)
 @post JSObject(#o) * DataProp(#o, "kind", "conflict") * DataProp(#o, "actual", null) * JSObject(#i) * DataProp(#i, "local", #v) * types(#v: Str) * GlobalObject() * ObjectPrototype($lobj_proto) * (ret == #o)

 @pre (outcome == #o) * (intent == #i) * JSObject(#o) * DataProp(#o, "kind", #k) * types(#k: Str) * (! (#k == "conflict")) * JSObject(#i) * DataProp(#i, "local", #v) * types(#v: Str) * GlobalObject() * ObjectPrototype($lobj_proto)
 @post JSObject(#o) * DataProp(#o, "kind", #k) * types(#k: Str) * (! (#k == "conflict")) * JSObject(#i) * DataProp(#i, "local", #v) * types(#v: Str) * GlobalObject() * ObjectPrototype($lobj_proto) * (ret == #o)

 */
