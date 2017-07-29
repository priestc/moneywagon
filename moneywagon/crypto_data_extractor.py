import requests
import re

def extract_crypto_data(github_path):
    """
    github_path can must be path on github, such as
    "bitcoin/bitcoin" or "litecoin-project/litecoin"
    """
    data = {'github_link': 'https://github.com/%s' % github_path}
    url = "https://raw.githubusercontent.com/%s/master/src/chainparams.cpp" % github_path
    content = requests.get(url).content
    #return content
    m = re.search("base58Prefixes\[PUBKEY_ADDRESS\] = std::vector<unsigned char>\(1,(\d+)\);", content)
    data['address_version_byte'] = int(m.groups()[0])

    m = re.search("base58Prefixes\[SCRIPT_ADDRESS\] = std::vector<unsigned char>\(1,(\d+)\);", content)
    data['script_hash_byte'] = int(m.groups()[0])

    m = re.search("base58Prefixes\[SECRET_KEY\] =\s+std::vector<unsigned char>\(1,(\d+)\);", content)
    data['private_key_prefix'] = int(m.groups()[0])

    data['message_magic'] = b""
    for index in range(4):
        m = re.search("pchMessageStart\[%s\] = 0x([\d\w]+);" % index, content)
        data['message_magic'] += bytes(m.groups()[0])

    data['seeds'] = []
    seed_index = 0
    # newest seed definition style
    m = re.findall('vSeeds.emplace_back\("([\w\d.]+)", (true|false)\);', content)
    print m
    if not m:
        # older style seed definition
        m = re.findall('vSeeds.push_back\(CDNSSeedData\("([\w\d.-]+)", "([-\w\d.-]+)"(, true|)\)\);', content)
        seed_index = 1
        print m

    for seed in m:
        if 'test' not in seed[seed_index]:
            data['seeds'].append(seed[seed_index])

    return data
