# Compile Toxygen

You can compile Toxygen using [PyInstaller](http://www.pyinstaller.org/)

Use Dockerfile and build script from `build` directory:

1. Build image:
```
docker build -t toxygen .
```

2. Run container:
```
docker run -it toxygen bash
```

3. Execute `build.sh` script:

```./build.sh```
