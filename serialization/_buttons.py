import base64

from telethon.tl.types import (
    KeyboardButton,
    KeyboardButtonBuy,
    KeyboardButtonCallback,
    KeyboardButtonCopy,
    KeyboardButtonGame,
    KeyboardButtonRequestGeoLocation,
    KeyboardButtonRequestPeer,
    KeyboardButtonRequestPhone,
    KeyboardButtonRequestPoll,
    KeyboardButtonRow,
    KeyboardButtonSimpleWebView,
    KeyboardButtonSwitchInline,
    KeyboardButtonUrl,
    KeyboardButtonUrlAuth,
    KeyboardButtonUserProfile,
    KeyboardButtonWebView,
)


def __serialize_buttons(rows: list[KeyboardButtonRow]) -> list[list[dict[str, str]]]:
    data: list[list[dict[str, str]]] = []
    for row in rows:
        row_data: list[dict[str, str]] = []
        for button in row.buttons:
            button_type = __button_type(button)
            button_data: dict[str, str] = {
                "type": button_type,
            }

            if hasattr(button, "text") and button.text:
                button_data["text"] = button.text

            button_data |= __button_data(button)

            if hasattr(button, "fwd_text") and button.fwd_text:
                button_data["forward_text"] = button.fwd_text

            if hasattr(button, "button_id") and button.button_id:
                button_data["button_id"] = str(button.button_id)

            row_data.append(button_data)
        data.append(row_data)
    return data


def __button_type(button: KeyboardButton) -> str:
    match button:
        case KeyboardButtonBuy():
            return "buy"
        case KeyboardButtonCopy():
            return "copy_text"
        case KeyboardButtonCallback():
            return "callback_with_password" if button.requires_password else "callback"
        case KeyboardButtonGame():
            return "game"
        case KeyboardButtonRequestGeoLocation():
            return "request_location"
        case KeyboardButtonRequestPeer():
            return "request_peer"
        case KeyboardButtonRequestPhone():
            return "request_phone"
        case KeyboardButtonRequestPoll():
            return "request_poll"
        case KeyboardButtonSimpleWebView():
            return "simple_web_view"
        case KeyboardButtonSwitchInline():
            return "switch_inline_same" if button.same_peer else "switch_inline"
        case KeyboardButtonUrl():
            return "url"
        case KeyboardButtonUrlAuth():
            return "auth"
        case KeyboardButtonUserProfile():
            return "user_profile"
        case KeyboardButtonWebView():
            return "web_view"
        case _:
            return "default"


def __button_data(button: KeyboardButton) -> dict[str, str]:
    match button:
        case KeyboardButtonCallback():
            return {
                "data": "",
                "dataBase64": base64.b64encode(button.data).decode(),
            }
        case (
            KeyboardButtonUrl()
            | KeyboardButtonUrlAuth()
            | KeyboardButtonWebView()
            | KeyboardButtonSimpleWebView()
        ):
            return {"data": button.url}
        case KeyboardButtonCopy():
            return {"data": button.copy_text}
        case KeyboardButtonUserProfile():
            return {"data": button.user_id}
        case KeyboardButtonSwitchInline():
            return {"data": button.query}
        case _:
            return {}
