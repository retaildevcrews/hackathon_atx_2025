# >>> Poetry auto-activate (injected by devcontainer)
function _poetry_auto_activate() {
  local _po_env
  _po_env=$(poetry env info --path 2>/dev/null)
  if [[ -n "$_po_env" && -f "$_po_env/bin/activate" ]]; then
    # shellcheck disable=SC1090
    source "$_po_env/bin/activate"
  fi
}
precmd_functions+=(_poetry_auto_activate)
# <<< Poetry auto-activate
