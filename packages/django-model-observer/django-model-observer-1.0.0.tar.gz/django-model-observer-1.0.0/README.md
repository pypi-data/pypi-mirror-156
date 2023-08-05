# Наблюдатель за моделями Django
## Использование

models.py:
    
    from django_model_observer import (
        ModelObserverBase,
        ModelOnlyObserverMixin,
        OriginalObjectMixin.
    )

    class UnitObserver(
        OriginalObjectMixin,
        ModelOnlyObserverMixin,
        ModelObserverBase
    ):
    
        """Наблюдатель за моделью Организация."""
    
        def post_save(self, instance, context, created, **_):
           ...
    
    
    unit_observer = UnitObserver()
    unit_observer.observe(Unit)