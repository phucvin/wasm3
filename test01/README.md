cd ..

mkdir -p build

cd build

cmake ..

make -j8

cd ..

build/wasm3 test/lang/fib.c.wasm

```
$ time build/wasm3 --func fib test/lang/fib32.wasm 40
Result: 102334155
real    0m6.090s

$ build/wasm3 --repl test/lang/fib32.wasm
wasm3> fib 6
Result: 8
```

mkdir tmp01

cd tmp01

git clone https://github.com/wasm3/wasm3-self-compiling

cd wasm3-self-compiling

cp /workspaces/wasm3/build/wasm3 ./bin/

make

got error, similar to https://github.com/wasm3/wasm3-self-compiling/issues/1, not sure how to fix