# checkmk-freeswitch
Basic Freeswitch plugin for CheckMK

For now, we are able to check the failed calls in and out again warn and crit levels from the config.ini.
These are set to 50% for critical and 30% for warn by default.

Typical output:
 - High inbound call failure 39%; High outbound call failure 36%;

We collect switch and gateway status and work is underway to expose those somehow.

This is a version 2 plugin and as such will not work with older installs, e.g. 1.6.X or older.

Please review the available documentation for installation at https://checkmk.com/.

Basically, the agent plugin would normally go into /usr/lib/check_mk_agent/plugins on the pbx.

For the checkmk server, I would clone the repo somewhere, e.g. /opt, and then:

  1. cd /opt/omd/sites/SITE_NAME/local/lib/python3/cmk/base/plugins/agent_based/
  2. ln -s /opt/checkmk-freeswitch/checks/freeswitch.py

