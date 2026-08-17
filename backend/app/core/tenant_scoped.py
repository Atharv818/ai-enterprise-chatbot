from typing import TypeVar, Type

T = TypeVar("T")


def create_tenant_scoped(model_class: Type[T], tenant_id: str, **kwargs) -> T:
    """
    Creates an instance of a tenant-scoped model, forcing tenant_id
    to always be explicitly provided. Prevents the 'forgot tenant_id'
    class of bug by making the correct pattern the easy pattern.
    """
    if not tenant_id:
        raise ValueError(f"tenant_id is required to create {model_class.__name__}")
    return model_class(tenant_id=tenant_id, **kwargs)

