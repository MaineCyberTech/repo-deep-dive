#!/usr/bin/env bash
# Forced-command wrapper for the scoped labvpn identity.
# Installed as /usr/local/bin/labvpn-run and referenced from authorized_keys
# command="...". It performs NO shell evaluation of the client-supplied command:
# arguments are split with bash `read -r -a` and validated before use.
#
# Allowed exactly:
#   list-agents
#   health
#   add-agent <name> [<pubkey>]
#   revoke-agent <name>
#   get-client <name>
# Everything else is denied (non-zero, message to stderr).
set -u

LIB=/usr/local/lib/labvpn

deny() { echo "DENIED: $*" >&2; exit 64; }

raw="${SSH_ORIGINAL_COMMAND:-}"
[ -n "$raw" ] || deny "no command supplied"
case "$raw" in
  *$'\n'*|*$'\r'*) deny "multi-line input rejected" ;;
esac

# Command-injection safe parse: no eval, no shell expansion.
read -r -a argv <<< "$raw"
cmd="${argv[0]:-}"

name_re='^[A-Za-z0-9_.-]{1,32}$'
pub_re='^[A-Za-z0-9+/]{42,44}=?$'

case "$cmd" in
  list-agents)
    [ "${#argv[@]}" -eq 1 ] || deny "list-agents takes no arguments"
    exec sudo -n "$LIB/list-agents.sh"
    ;;
  health)
    [ "${#argv[@]}" -eq 1 ] || deny "health takes no arguments"
    exec sudo -n "$LIB/verify.sh"
    ;;
  add-agent)
    [ "${#argv[@]}" -ge 2 ] && [ "${#argv[@]}" -le 3 ] || deny "usage: add-agent <name> [<pubkey>]"
    name="${argv[1]}"
    [[ "$name" =~ $name_re ]] || deny "invalid agent name"
    if [ "${#argv[@]}" -eq 3 ]; then
      pub="${argv[2]}"
      [[ "$pub" =~ $pub_re ]] || deny "invalid public key"
      exec sudo -n "$LIB/add-agent.sh" "$name" "$pub"
    else
      exec sudo -n "$LIB/add-agent.sh" "$name"
    fi
    ;;
  revoke-agent)
    [ "${#argv[@]}" -eq 2 ] || deny "usage: revoke-agent <name>"
    name="${argv[1]}"
    [[ "$name" =~ $name_re ]] || deny "invalid agent name"
    exec sudo -n "$LIB/revoke-agent.sh" "$name"
    ;;
  get-client)
    [ "${#argv[@]}" -eq 2 ] || deny "usage: get-client <name>"
    name="${argv[1]}"
    [[ "$name" =~ $name_re ]] || deny "invalid agent name"
    exec sudo -n "$LIB/get-client.sh" "$name"
    ;;
  *)
    deny "unsupported command: ${cmd:-<empty>}"
    ;;
esac
