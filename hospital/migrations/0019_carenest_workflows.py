from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def copy_legacy_appointment_values(apps, schema_editor):
    Appointment = apps.get_model('hospital', 'Appointment')
    for appointment in Appointment.objects.all().iterator():
        appointment.scheduled_date = appointment.appointmentDate
        appointment.workflow_status = 'APPROVED' if appointment.status else 'PENDING'
        appointment.save(update_fields=['scheduled_date', 'workflow_status'])


class Migration(migrations.Migration):
    dependencies = [
        ('hospital', '0018_auto_20201015_2036'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='scheduled_date',
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
        migrations.AddField(
            model_name='appointment',
            name='scheduled_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='workflow_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('COMPLETED', 'Completed')], default='PENDING', max_length=12),
        ),
        migrations.RunPython(copy_legacy_appointment_values, migrations.RunPython.noop),
        migrations.CreateModel(
            name='DoctorAvailability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.PositiveSmallIntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability', to='hospital.doctor')),
            ],
            options={'ordering': ['weekday', 'start_time']},
        ),
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diagnosis', models.CharField(max_length=200)),
                ('prescription', models.TextField()),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_medical_records', to='hospital.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_records', to='hospital.patient')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddConstraint(
            model_name='doctoravailability',
            constraint=models.UniqueConstraint(fields=('doctor', 'weekday', 'start_time', 'end_time'), name='unique_doctor_availability'),
        ),
    ]
