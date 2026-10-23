/**
 @id blobIntentResendable

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #a) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#p <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#p <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#a <# #p)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#a <# #p) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #a) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#p <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#p <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#a <# #p)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#a <# #p) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #a) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#p <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#p <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#a <# #p)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "pending") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#a <# #p) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * ((#o, "notAppliedThrough") -> none) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", undefined) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", 0)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", 0) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "notAppliedThrough", null) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * (0 <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #a) * (ret == true)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#p <# #a)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#p <# #a) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#a <# #p)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", "unknown") * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (#a <# #p) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * ((#o, "notAppliedThrough") -> none)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * ((#o, "notAppliedThrough") -> none) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", undefined)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", undefined) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", null)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", null) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * ((#o, "receipt") -> none) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * ((#o, "notAppliedThrough") -> none)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * ((#o, "notAppliedThrough") -> none) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", undefined)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", undefined) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", null)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", null) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", undefined) * DataProp(#o, "state", #s) * types(#s: Str) * (! (#s == "pending")) * (! (#s == "unknown")) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", #r) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * types(#r: Obj) * ((#o, "notAppliedThrough") -> none)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", #r) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * types(#r: Obj) * ((#o, "notAppliedThrough") -> none) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", #r) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * types(#r: Obj) * DataProp(#o, "notAppliedThrough", undefined)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", #r) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * types(#r: Obj) * DataProp(#o, "notAppliedThrough", undefined) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", #r) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * types(#r: Obj) * DataProp(#o, "notAppliedThrough", null)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", #r) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * types(#r: Obj) * DataProp(#o, "notAppliedThrough", null) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", #r) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * types(#r: Obj) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", #r) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * types(#r: Obj) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", null) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * ((#o, "notAppliedThrough") -> none)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", null) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * ((#o, "notAppliedThrough") -> none) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", null) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", undefined)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", null) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", undefined) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", null) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", null)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", null) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", null) * (ret == false)

 @pre (row == #o) * JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", null) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991)
 @post JSObject(#o) * GlobalObject() * ObjectPrototype($lobj_proto) * DataProp(#o, "receipt", null) * DataProp(#o, "state", #s) * types(#s: Str) * DataProp(#o, "attempts", #a) * types(#a: Num) * (0 <=# #a) * (#a <=# 9007199254740991) * DataProp(#o, "notAppliedThrough", #p) * types(#p: Num) * (0 <=# #p) * (#p <=# 9007199254740991) * (ret == false)
 */
