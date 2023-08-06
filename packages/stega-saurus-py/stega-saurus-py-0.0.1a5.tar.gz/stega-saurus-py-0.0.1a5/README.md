# stega-saurus
A CLI to perform steganography


## Installation

```
pip install stega-saurus-py
```

## Usage

### Command help

View help and available commands for the `stega` CLI

```
python -m stega --help
```

View command help, in this case `textimg` and it's sub commands

```
python -m stega textimg --help
```

giving output

```
Usage: stega textimg [OPTIONS] COMMAND [ARGS]...

  Stega-saurus text image steganography

Options:
  --version
  --help     Show this message and exit.

Commands:
  decode  Decode a message from an image
  encode  Encode a message using an image output as a PNG
```

that lists the `textimg` command's sub commands `encode` and `decode`.

View a sub command's help e.g. the `encode` sub command of `textimg`

```
python -m stega textimg encode --help
``` 

producing the output with full sub command usage

```
Usage: stega textimg encode [OPTIONS] IN_IMAGE_PATH OUT_IMAGE_PATH MSG

  Encode a message using an image output as a PNG

Arguments:
  IN_IMAGE_PATH   Original image path to use in encoding  [required]
  OUT_IMAGE_PATH  Output image path to encode the message into (file
                  extension ignored, image will be a png)  [required]
  MSG             Message to encode in to the image  [required]

Options:
  --help  Show this message and exit.
```


### Text image steganography

Encode a message in an image, outputting the result as a png 

```
python -m stega textimg encode ~/Desktop/inimg.jpg ~/Desktop/outimg.png "Your secret message goes here"
```

This command will produce output that contains a key that will need to be used to decode the message from the png image

```
stega-saurus text image steganography encode
Encoding...
Done encoding
Decode key: cj
``` 

To decode the message from the image above run the `textimg`  `decode` command and decode key

```
python -m stega textimg decode ~/Desktop/outimg.png cj
```

outputting the encoded message 

```
stega-saurus text image steganography decode
Decoding...
Done decoding
Encoded message:
Your secret message goes here
```
