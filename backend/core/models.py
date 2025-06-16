from django.db import models

class Job(models.Model):
    position = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    position_url = models.URLField(max_length=255)
    company_url = models.URLField(max_length=255)
    published_date = models.CharField(null=True, blank=True)
    end_date = models.CharField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'hr_ge'