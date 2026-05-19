from datetime import date

from pydantic import ValidationError


def validation_errors_dict(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for item in exc.errors():
        field = item['loc'][-1] if item['loc'] else '_form'
        key = str(field)
        msg = item.get('msg', 'Некорректное значение')
        if msg.startswith('Value error, '):
            msg = msg.removeprefix('Value error, ')
        errors[key] = msg
    return errors


def today_iso() -> str:
    return date.today().isoformat()
