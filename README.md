# Torch API
<img alt="v0.1.0" src="https://img.shields.io/badge/v-0.1.0-brightgreen">

## Contract
### Request
```json
{
    "request": "<REQUEST>",
    "image": "<IMAGE_BASE64>"
}
```
### Response
```json
{
    "response": "<RESPONSE>",
    "error": "<ERROR_MESSAGE>"
}
```
### Valid values
#### Image format
`"<IMAGE_BASE64>"` is a base-64 encoding of the image that will be analyzed. The
image must be **224 px by 224** px and contain **RGB** channels.
#### Services
|Service           |Request   |Response type|Response                                     |
|------------------|----------|:-----------:|---------------------------------------------|
|Banknote detection|`banknote`|`int`        |`5` \| `10` \| `20` \| `50` \| `100` \| `200`|
#### Errors
`<RESPONSE>` is `"invalid request"` if any problem is faced with the parsing the
request.
|Error message    |Reason                                                 |
|-----------------|-------------------------------------------------------|
|`Unknown service`|The requested service is not one of those listed above.|