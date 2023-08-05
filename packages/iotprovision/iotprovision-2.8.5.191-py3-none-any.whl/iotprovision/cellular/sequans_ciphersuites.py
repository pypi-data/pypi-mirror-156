
SEQUANS_CIPHERSUITES = {
    0x1301: "TLS_AES_128_GCM_SHA256",
    0x1302: "TLS_AES_256_GCM_SHA384",
    0x1303: "TLS_CHACHA20_POLY1305_SHA256",
    0x1304: "TLS_AES_128_CCM_SHA256",
    0x1305: "TLS_AES_128_CCM_8_SHA256",
    0x000A: "TLS_RSA_WITH_3DES_EDE_CBC_SHA",
    0x002F: "TLS_RSA_WITH_AES_128_CBC_SHA",
    0x0035: "TLS_RSA_WITH_AES_256_CBC_SHA",
    0x0033: "TLS_DHE_RSA_WITH_AES_128_CBC_SHA",
    0x0039: "TLS_DHE_RSA_WITH_AES_256_CBC_SHA",
    0x00AB: "TLS_DHE_PSK_WITH_AES_256_GCM_SHA384",
    0x00AA: "TLS_DHE_PSK_WITH_AES_128_GCM_SHA256",
    0x00A9: "TLS_PSK_WITH_AES_256_GCM_SHA384",
    0x00A8: "TLS_PSK_WITH_AES_128_GCM_SHA256",
    0x00B3: "TLS_DHE_PSK_WITH_AES_256_CBC_SHA384",
    0x00B2: "TLS_DHE_PSK_WITH_AES_128_CBC_SHA256",
    0x00AF: "TLS_PSK_WITH_AES_256_CBC_SHA384",
    0x00AE: "TLS_PSK_WITH_AES_128_CBC_SHA256",
    0x008C: "TLS_PSK_WITH_AES_128_CBC_SHA",
    0x008D: "TLS_PSK_WITH_AES_256_CBC_SHA",
    0xC0A6: "TLS_DHE_PSK_WITH_AES_128_CCM",
    0xC0A7: "TLS_DHE_PSK_WITH_AES_256_CCM",
    0xC0A4: "TLS_PSK_WITH_AES_128_CCM",
    0xC0A5: "TLS_PSK_WITH_AES_256_CCM",
    0xC0A8: "TLS_PSK_WITH_AES_128_CCM_8",
    0xC0A9: "TLS_PSK_WITH_AES_256_CCM_8",
    0xC0A0: "TLS_RSA_WITH_AES_128_CCM_8",
    0xC0A1: "TLS_RSA_WITH_AES_256_CCM_8",
    0xC0AC: "TLS_ECDHE_ECDSA_WITH_AES_128_CCM",
    0xC0AE: "TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8",
    0xC0AF: "TLS_ECDHE_ECDSA_WITH_AES_256_CCM_8",
    0xC013: "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
    0xC014: "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
    0xC009: "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
    0xC00A: "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
    0xC012: "TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA",
    0xC008: "TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA",
    0x003C: "TLS_RSA_WITH_AES_128_CBC_SHA256",
    0x003D: "TLS_RSA_WITH_AES_256_CBC_SHA256",
    0x0067: "TLS_DHE_RSA_WITH_AES_128_CBC_SHA256",
    0x006B: "TLS_DHE_RSA_WITH_AES_256_CBC_SHA256",
    0x009C: "TLS_RSA_WITH_AES_128_GCM_SHA256",
    0x009D: "TLS_RSA_WITH_AES_256_GCM_SHA384",
    0x009E: "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
    0x009F: "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384",
    0xC02F: "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    0xC030: "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    0xC02B: "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    0xC02C: "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    0xC027: "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
    0xC023: "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
    0xC028: "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
    0xC024: "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384",
    0xCCA8: "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
    0xCCA9: "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
    0xCCAA: "TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
    0xCC13: "TLS_ECDHE_RSA_WITH_CHACHA20_OLD_POLY1305_SHA256",
    0xCC14: "TLS_ECDHE_ECDSA_WITH_CHACHA20_OLD_POLY1305_SHA256",
    0xCC15: "TLS_DHE_RSA_WITH_CHACHA20_OLD_POLY1305_SHA256",
    0xC037: "TLS_ECDHE_PSK_WITH_AES_128_CBC_SHA256",
    0xCCAB: "TLS_PSK_WITH_CHACHA20_POLY1305_SHA256",
    0xCCAC: "TLS_ECDHE_PSK_WITH_CHACHA20_POLY1305_SHA256",
    0xCCAD: "TLS_DHE_PSK_WITH_CHACHA20_POLY1305_SHA256",
    0x0016: "TLS_DHE_RSA_WITH_3DES_EDE_CBC_SHA",
}

# default ciphersuites per cloud provider. Used if none is specified on connand line
DEFAULT_CIPHERSUITES = {"aws": ["TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                                # Adding the below causes MQTT connect to fail
                                # "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
                                ],
                        "azure": ["TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                                  "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"],
                        "google": ["TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                                   "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"]}

def get_ciphersuite(cipher):
    """
    Provide value and name for a ciphersuite supported by Sequans modem.

    :param cipher: Name or integer value of a ciphersuite
    :return: (value, name) tuple of strings representing found ciphersuite
    """
    for value, name in SEQUANS_CIPHERSUITES.items():
        try:
            cipherint = int(cipher, 0)
        except ValueError:
            cipherint = None
        if cipherint == value or cipher.upper() == name:
            return (f"0x{value:04x}", name)
    return (None, None)

def print_ciphersuites():
    """
    Print list of supported ciphersuites
    """
    print("\nValid ciphersuites are:")
    for value, name in SEQUANS_CIPHERSUITES.items():
        print(f"0x{value:04x}  {name}")
    print("\nProvide either the hex value or name of ciphersuites separated with comma (',')")

def validate_ciphersuites(ciphersuites):
    """
    Validate ciphersuites given as name or numeric (hex) value.

    :param ciphersuites: List of strings with ciphesrsuites (internal)
                         or single string with comma-separated list of ciphersuites (CLI).
    """
    if not ciphersuites:
        return []
    valid = []
    invalid = []
    if isinstance(ciphersuites, str):
        # convert to internal representation
        ciphersuites =  ciphersuites.split(",")
    for cipher in ciphersuites:
        value, name = get_ciphersuite(cipher)
        if value is None:
            invalid.append(cipher)
        else:
            valid.append(value)
    if invalid:
        raise ValueError(f"Invalid ciphersuite(s): {','.join(invalid)}")
    return valid
