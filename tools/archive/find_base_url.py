import re

for fname in ['chunk_7936.js', 'chunks/b9e39b43-b5eda7c146674b07.js']:
    with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    matches = re.findall(r'baseUrl\s*:\s*[`"\']([^`"\']+)[\'"`]', code)
    print(f"Base URLs in {fname}:", set(matches))
    
    # search for sdp project or sdp_project
    sdp_matches = re.findall(r'SDP_PROJECT\s*:\s*[`"\']([^`"\']+)[\'"`]', code)
    print(f"SDP_PROJECT in {fname}:", set(sdp_matches))
