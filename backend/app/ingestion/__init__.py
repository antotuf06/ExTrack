"""Source adapters and the ingestion pipeline.

Adapters turn a source (Excel, bank PDF/CSV, manual form) into ``RawTransaction``
objects and never write to the database. The pipeline does
normalize → deduplicate → categorize → save, recording an ``import_batch``.
"""
