import requests
import re

def get_content_from_github(github_path, file):
    url = "https://raw.githubusercontent.com/%s/master/src/%s" % (github_path, file)
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.content

def extract_crypto_data(github_path):
    """
    github_path can must be path on github, such as
    "bitcoin/bitcoin" or "litecoin-project/litecoin"
    """
    data = {'github_link': 'https://github.com/%s' % github_path}

    content = get_content_from_github(github_path, "chainparams.cpp")
    if content:
        data.update(_get_from_chainparams(content))
    else:
        content = get_content_from_github(github_path, "base58.h")
        if content:
            data.update(_get_from_base58h(content))

    content = get_content_from_github(github_path, "main.cpp")
    if content:
        data.update(_get_from_main(content))

    return data

def _get_from_main(content):
    data = {}
    match = test_regexes(content,
        "if\s+\(txPrev\.nTime\s+>\s+nTime\)", # peercoin style PoS
        "if\s+\(\(unsigned int\)coins\.nTime\s+>\s+tx\.nTime\)" # rdd style PoSV
    )
    if match:
        data['transaction_form'] = 'ppc-timestamp'

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
    match = test_regexes(content,
        "base58Prefixes\[PUBKEY_ADDRESS\]\s+=\s+std::vector<unsigned char>\(1,(\d+)\);",
        "base58Prefixes\[PUBKEY_ADDRESS\]\s+=\s+list_of\((\d+)\).convert_to_container<std::vector<unsigned char> >\(\);",
        "base58Prefixes\[PUBKEY_ADDRESS\]\s+=\s+list_of\((\d+)\);"
    )
    if match:
        data['address_version_byte'] = int(match)

    match = test_regexes(content,
        "base58Prefixes\[SCRIPT_ADDRESS\]\s+=\s+std::vector<unsigned char>\(1,(\d+)\);",
        "base58Prefixes\[SCRIPT_ADDRESS\]\s+=\s+list_of\((\d+)\).convert_to_container<std::vector<unsigned char> >\(\);",
        "base58Prefixes\[SCRIPT_ADDRESS\]\s+=\s+list_of\((\d+)\);"
    )
    if match:
        data['script_hash_byte'] = int(match)

    match = test_regexes(content,
        "base58Prefixes\[SECRET_KEY\]\s+=\s+std::vector<unsigned char>\(1,(\d+)\);",
        "base58Prefixes\[SECRET_KEY\]\s+=\s+list_of\((\d+)\).convert_to_container<std::vector<unsigned char> >\(\);",
        "base58Prefixes\[SECRET_KEY\]\s+=\s+list_of\((\d+)\);"
    )
    if match:
        data['private_key_prefix'] = int(match)

    try:
        data['message_magic'] = b""
        for index in range(4):
            m = re.search("pchMessageStart\[%s\] = 0x([\d\w]+);" % index, content)
            data['message_magic'] += bytes(m.groups()[0])
    except:
        pass
    
    data['seed_nodes'] = []
    seed_index = 0
    # newest seed definition style
    m = re.findall('vSeeds.emplace_back\("([\w\d.]+)", (true|false)\);', content)

    if not m:
        # older style seed definition
        m = re.findall('vSeeds.push_back\(CDNSSeedData\("([\w\d.-]+)", "([-\w\d.-]+)"(, true|)\)\);', content)
        seed_index = 1

    for seed in m:
        if 'test' not in seed[seed_index]:
            data['seed_nodes'].append(seed[seed_index])

    return data


def test_regexes(content, *regexes):
    for regex in regexes:
        m = re.search(regex, content)
        if m:
            return m.groups()[0] if len(m.groups()) else True

def crawl_SLIP44():
    from bs4 import BeautifulSoup
    url = "https://github.com/satoshilabs/slips/blob/master/slip-0044.md"
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    table = soup.article.find("table")

    coins = {}
    for i, row in enumerate(table.find_all("tr")):
        if i == 0:
            continue # skip header row

        tds = row.find_all("td")
        index, symbol, name = int(tds[0].string), tds[2].string, tds[3].string
        if symbol: # ignore lines with no symbol
            coins[symbol.lower()] = (index, name)

    return coins
