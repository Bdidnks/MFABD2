"""AUTO-MAS compatibility for MFABD2's existing account selection API.

Keep all original game pipelines. Restore PI option injection and use an entry
guard whose False result is a real MaaFramework task failure (not StopTask).
"""
import hashlib
import json

SWITCH = "启用多存档"
INPUT_OPTION = "存档名称"
INPUT_FIELD = "账号多开配置"
INJECT = "Agt_MultiSave_Inject"
PREFIX = "MAS_AccountGate__"
GATE_FILE = "resource/base/pipeline/MAS_AccountGate.json"


def adapt_interface(doc):
    options = doc.get("option", {})
    switch = options.get(SWITCH, {})
    field = options.get(INPUT_OPTION, {})
    cases = switch.get("cases", [])
    if switch.get("type") != "switch" or {c.get("name") for c in cases} != {"Yes", "No"}:
        raise ValueError("Account switch layout changed; review compatibility patch")
    if field.get("type") != "input" or not any(i.get("name") == INPUT_FIELD for i in field.get("inputs", [])):
        raise ValueError("Account input layout changed; review compatibility patch")
    if SWITCH in doc.get("global_option", []):
        raise ValueError("Upstream now declares account settings globally; review/remove our patch")
    if field.get("pipeline_override") or any(c.get("pipeline_override") for c in cases):
        raise ValueError("Upstream account injection changed; review/remove our patch")
    doc.setdefault("global_option", []).append(SWITCH)
    field["pipeline_override"] = {INJECT: {"attach": {"account_id": "{" + INPUT_FIELD + "}"}}}
    for case in cases:
        if case["name"] == "No":
            case["pipeline_override"] = {INJECT: {"attach": {"account_id": "0"}}}
    for task in doc.get("task", []):
        entry = task.get("entry")
        if not isinstance(entry, str) or not entry or entry.startswith(PREFIX):
            raise ValueError("Unexpected task entry")
        # It remains a harmless settings task. Its saved options migrate into
        # MAS globalOptions through the host's normal PI configuration loader.
        if entry == "Env_MultiSave_Config":
            task["option"] = [name for name in task.get("option", []) if name != SWITCH]
        else:
            task["entry"] = PREFIX + entry
    return doc


def gate_pipeline(doc):
    gates = {}
    for task in doc["task"]:
        entry = task["entry"]
        if entry.startswith(PREFIX):
            gates[entry] = {
                "recognition": "DirectHit",
                "action": "Custom",
                "custom_action": "SwitchAccountCheckpoint",
                "focus": "检查任务存档配置",
                "next": [entry[len(PREFIX):]],
                "on_error": [],
                "pre_delay": 0,
                "post_delay": 0,
            }
    if not gates:
        raise ValueError("No account guards generated")
    return (json.dumps(gates, ensure_ascii=False, indent=4) + "\n").encode("utf8")


def patch_account_sync(raw):
    text = raw.decode("utf-8-sig")
    start = '        try:\n            result = context.run_action(STOP_ENTRY)'
    end = '        return False'
    if text.count(start) != 1:
        raise ValueError("Upstream account failure handler changed; review/remove our patch")
    begin = text.index(start)
    finish = text.index(end, begin) + len(end)
    text = text[:begin] + (
        '        # A False entry-guard result is reported as Tasker.Task.Failed.\n'
        '        # StopTask would instead report Tasker.Task.Succeeded in MaaFW 5.14.3.\n'
        '        return False'
    ) + text[finish:]
    compile(text, "account_sync.py", "exec")
    return text.encode("utf8")
