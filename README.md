# InspIRCd Authentication Gate Configuration Generator
*Yes, the naming is not the best but so be it.*

This is a Python script that generates connect blocks to require SASL authentication for provided IP addresses/ranges.

One such use case is to restrict connectivity of known VPN providers as they are often vectors for abuse on IRC. Authentication gates can serve as a middle ground for allowing legitimate connections.

To see the available help options, run the script with `--help`.

## Example IP Lists
- https://github.com/X4BNet/lists_vpn/
