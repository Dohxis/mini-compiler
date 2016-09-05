## Todo

- [x] Variable assignment [~~Parsing~~ / ~~Codegen~~];<br>
```
variable :Int = 123;
variable :Int[] = [123, 123];
```
- [x] Function call [~~Parsing~~ / ~~Codegen~~];<br>
```
func(arg1, arg2);
__stdio::printf("%d\n", variable);
```
- [x] Function declaration [Parsing / Codegen];<br>
```
function foo(x:Int) {  }
function bar() :Int {  }
```
- [ ] For and while loops [Parsing / Codegen];<br>
```
for(x in 0..10) {  }
while(variable) {  }
```
- [ ] If/else clauses [Parsing / Codegen];<br>
```
if(variable) {  } else {  }
```
