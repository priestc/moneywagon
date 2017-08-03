import requests
import re

def extract_crypto_data(github_path):
    """
    github_path can must be path on github, such as
    "bitcoin/bitcoin" or "litecoin-project/litecoin"
    """
    data = {'github_link': 'https://github.com/%s' % github_path}
    url = "https://raw.githubusercontent.com/%s/master/src/chainparams.cpp" % github_path
    response = requests.get(url)
    content = response.content
    #return content

    if response.status_code == 200:
        data.update(_get_from_chainparams(content))
    else:
        url = "https://raw.githubusercontent.com/%s/master/src/base58.h" % github_path
        response = requests.get(url)
        content = response.content

        if response.status_code == 200:
            data.update(_get_from_base58h(content))

    return data

def _get_from_base58h(content):
    data = {}
    m = re.search("PUBKEY_ADDRESS = (\d+),", content)
    if m:
        data['address_version_byte'] = int(m.groups()[0])

    if "PRIVKEY_ADDRESS = CBitcoinAddress::PUBKEY_ADDRESS + 128," in content:
        data['private_key_prefix'] = data['address_version_byte'] + 128

    if "SetData(128 + (fTestNet ? CBitcoinAddress::PUBKEY_ADDRESS_TEST : CBitcoinAddress::PUBKEY_ADDRESS), &vchSecret[0], vchSecret.size());" in content:
        data['private_key_prefix'] = data['address_version_byte'] + 128

    m = re.search("SCRIPT_ADDRESS = (\d+), ", content)
    if m:
        data['script_hash_byte'] = int(m.groups()[0])

    return data


def _get_from_chainparams(content):
    # newer style "chain params" definitions.
    data = {}
    m = re.search("base58Prefixes\[PUBKEY_ADDRESS\]\s+=\s+std::vector<unsigned char>\(1,(\d+)\);", content)
    data['address_version_byte'] = int(m.groups()[0])

    m = re.search("base58Prefixes\[SCRIPT_ADDRESS\]\s+=\s+std::vector<unsigned char>\(1,(\d+)\);", content)
    data['script_hash_byte'] = int(m.groups()[0])

    m = re.search("base58Prefixes\[SECRET_KEY\]\s+=\s+std::vector<unsigned char>\(1,(\d+)\);", content)
    data['private_key_prefix'] = int(m.groups()[0])

    data['message_magic'] = b""
    for index in range(4):
        m = re.search("pchMessageStart\[%s\] = 0x([\d\w]+);" % index, content)
        data['message_magic'] += bytes(m.groups()[0])

    data['seeds'] = []
    seed_index = 0
    # newest seed definition style
    m = re.findall('vSeeds.emplace_back\("([\w\d.]+)", (true|false)\);', content)

    if not m:
        # older style seed definition
        m = re.findall('vSeeds.push_back\(CDNSSeedData\("([\w\d.-]+)", "([-\w\d.-]+)"(, true|)\)\);', content)
        seed_index = 1

    for seed in m:
        if 'test' not in seed[seed_index]:
            data['seeds'].append(seed[seed_index])

    return data
