# Image to cpp

Convert an image into a c++ header file containing a bytes array. Useful for electronic projects using a thermal printer or a LCD display.

## Usage

```
> image-to-cpp --help
usage: main.py [-h] [-r RESIZE] [-s] [-o OUTPUT] [-v] [-d] [-t THRESHOLD] image_path

Convert an image into a byte array c++ code.

positional arguments:
  image_path            Path of image to convert, use `--` to read from stdin.

optional arguments:
  -h, --help            show this help message and exit
  -r RESIZE, --resize RESIZE
                        Resize image to specified width, keeping aspect ratio.
  -s, --show            Only show converted image.
  -o OUTPUT, --output OUTPUT
                        Store to specified file (default: image_name.h), use `--` to output on stdout.
  -v, --verbose         Deactivate information messages.
  -d, --dither          Activate dithering.
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold level when converting to black and white, from 0 to 255 (default: 128).
```

## License

MIT
