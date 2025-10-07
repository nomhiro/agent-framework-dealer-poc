import logging
import sys
import json
from typing import Any


def configure_stdout_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    root.setLevel(level)
    # Avoid adding multiple handlers
    if any(isinstance(h, logging.StreamHandler) and getattr(h, "__copilot_stdout_handler", False) for h in root.handlers):
        return

    class StdoutHandler(logging.StreamHandler):
        """Handler that prints only TOOL and ARGS when present in the LogRecord."""

        def _find_tool_in_obj(self, obj: Any) -> tuple[str | None, Any | None]:
            if obj is None:
                return None, None
            if isinstance(obj, dict):
                t = obj.get("type") or obj.get("_type")
                if t in ("tool_call", "function_call"):
                    name = obj.get("name") or obj.get("function") or obj.get("id")
                    args = obj.get("arguments") or obj.get("input") or obj.get("args")
                    return name, args
                for v in obj.values():
                    name, args = self._find_tool_in_obj(v)
                    if name or args:
                        return name, args
            elif isinstance(obj, list):
                for item in obj:
                    name, args = self._find_tool_in_obj(item)
                    if name or args:
                        return name, args
            return None, None

        def emit(self, record: logging.LogRecord) -> None:
            try:
                stream = self.stream or sys.stdout
                tool_name = None
                tool_args = None

                # 1) record.msg is a dict
                try:
                    if isinstance(record.msg, dict):
                        tool_name, tool_args = self._find_tool_in_obj(record.msg)
                except Exception:
                    pass

                # 2) parse message text as JSON
                if not tool_name and not tool_args:
                    try:
                        parsed = json.loads(record.getMessage())
                        if isinstance(parsed, (dict, list)):
                            tool_name, tool_args = self._find_tool_in_obj(parsed)
                    except Exception:
                        pass

                # 3) inspect common custom dimensions
                if not tool_name and not tool_args:
                    cd = None
                    for key in ("customDimensions", "custom_dimensions", "customdims"):
                        if key in record.__dict__:
                            cd = record.__dict__.get(key)
                            break
                    if cd and isinstance(cd, dict):
                        name = cd.get("gen_ai.tool.name") or cd.get("tool.name") or cd.get("gen_ai.tool")
                        args = cd.get("gen_ai.tool.call.arguments") or cd.get("tool.arguments") or cd.get("arguments")
                        if name or args:
                            tool_name = name
                            tool_args = args
                    else:
                        for k, v in record.__dict__.items():
                            if isinstance(k, str) and ("gen_ai.tool.name" in k or k.endswith("tool.name") or "tool.call.arguments" in k):
                                if "name" in k:
                                    tool_name = v
                                else:
                                    tool_args = v

                # 4) crude fallback parsing from message text
                if not tool_name and not tool_args:
                    msg_text = record.getMessage()
                    if isinstance(msg_text, str) and ("function_call" in msg_text or "tool_call" in msg_text):
                        try:
                            start = msg_text.find("{")
                            if start != -1:
                                sub = msg_text[start:]
                                parsed = json.loads(sub)
                                tool_name, tool_args = self._find_tool_in_obj(parsed)
                        except Exception:
                            pass

                if tool_name or tool_args:
                    try:
                        args_str = json.dumps(tool_args, ensure_ascii=False) if isinstance(tool_args, (dict, list)) else str(tool_args)
                    except Exception:
                        args_str = repr(tool_args)
                    stream.write(f"TOOL={tool_name or 'unknown'} ARGS={args_str}\n")
            except Exception:
                # swallow any handler errors
                pass

    h = StdoutHandler(stream=sys.stdout)
    h.__copilot_stdout_handler = True
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    h.setFormatter(formatter)
    root.addHandler(h)
