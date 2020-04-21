# Torch API

<img alt="v0.1.0" src="https://img.shields.io/badge/v-0.1.0-brightgreen">

## Usage

Example usage:

```python
import torchapi

request =
  """
  {
    "request": "banknote",
    "image": "data:image/png;base64,iVBORw0KGg..."
  }
  """
response = torchapi.handle(request)
print(response)
```

Example output:

```json
{
  "status": "ok",
  "time": "2020-02-25 19:50:53.833346",
  "response": 100,
  "confidence": 0.78
}
```

## Contract

### Request

```json
{
  "request": "<REQUEST>",
  "image": "<IMAGE_BASE64>"
}
```

`"<IMAGE_BASE64>"` is a base-64 encoding of the image that will be analyzed. The
image must be **224px by 224px** and contain **RGB** channels.

The contents of the base-64 string must adhere to the following regex:

    ^data:image(/(.*))?;base64,(.+)$

### Response

```json
{
  "status": "<STATUS>",
  "time": "<SERVER_TIME>",
  "response": "<RESPONSE>",
  "confidence": "<CONFIDENCE>"
}
```

`confidence` is a number between 0 and 1 that indicates the level of confidence in the prediction.

### Valid values

When the server returns a valid response, the `"status"` is set to `"ok"`.

#### Services

| Service                       | Request    | Response                                              |
| ----------------------------- | ---------- | ----------------------------------------------------- |
| Banknote detection            | `banknote` | `5` \| `10` \| `20` \| `50` \| `100` \| `200` \| `bg` |
| Optical character recognition | `ocr`      | `'Lorem ipsum dolor'`                                 |

#### Errors

In the case of error, the response is sent as follows:

```json
{
  "status": "error",
  "time": "<SERVER_TIME>",
  "error_origin": "<ERROR_ORIGIN>",
  "error_message": "<ERROR_MESSAGE>"
}
```

Some of the errors and their meaning:

| Error message          | Origin   | Reason                                                                  |
| ---------------------- | -------- | ----------------------------------------------------------------------- |
| `Unknown service`      | `server` | The requested service is not one of those listed above.                 |
| `No image`             |          | A service requires image data but no `image` was passed in the request. |
| `Invalid image format` |          | The `image` in the request is not in the proper base-64 format.         |
