import argparse
import sys

def parse_config_file(input_file, output_file, server_name, skip_dupe_check):
    config_host_lines = []
    seen_mac = set()
    seen_ip = set()

    with open(input_file, 'r') as file:
        config_host = False
        for line in file.readlines():
            if line.strip() == 'config host':
                config_host = True
                host_data = {}
            elif config_host and line.strip().startswith('option'):
                option, value = line.strip().split(' ', 2)[1:]
                host_data[option] = value.strip('\'')
            elif config_host and line.strip() == '':
                config_host = False
                # Check for duplicates
                if not skip_dupe_check:
                    if 'mac' in host_data and 'ip' in host_data:
                        if host_data['mac'] in seen_mac:
                            raise ValueError(f"Duplicate MAC address found: {host_data['mac']}")
                        if host_data['ip'] in seen_ip:
                            raise ValueError(f"Duplicate IP address found: {host_data['ip']}")
                        seen_mac.add(host_data['mac'])
                        seen_ip.add(host_data['ip'])
                config_host_lines.append(host_data)
    
    with open(output_file, 'w') as file:
        file.write("/ip dhcp-server lease\n")
        for host in config_host_lines:
            if 'mac' in host and 'ip' in host:
                file.write(f"add mac-address={host['mac']} address={host['ip']} server={server_name}\n")


def main():
    parser = argparse.ArgumentParser(description='Parse OpenWRT DHCP configuration file.')
    parser.add_argument('input_file', help='The OpenWRT configuration file to parse.')
    parser.add_argument('output_file', help='The output file where to write the results.')
    parser.add_argument('-s', '--server_name', default='dhcp1', help='The server name to be written in the output file.')
    parser.add_argument('--skip_dupe_check', action='store_true', help='If provided, the duplicate check will be skipped.')

    args = parser.parse_args()

    if not args.input_file or not args.output_file:
        print('You must provide an input file and an output file.', file=sys.stderr)
        sys.exit(1)

    parse_config_file(args.input_file, args.output_file, args.server_name, args.skip_dupe_check)

if __name__ == '__main__':
    main()
