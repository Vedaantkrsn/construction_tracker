from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Attendance, AttendanceQRCode, Site, UserProfile


class AttendanceQRCodeTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username="manager", password="test-password")
        UserProfile.objects.create(user=self.manager, role="manager")
        self.worker = User.objects.create_user(username="worker", password="test-password")
        UserProfile.objects.create(user=self.worker, role="worker")
        self.unassigned_worker = User.objects.create_user(username="unassigned", password="test-password")
        UserProfile.objects.create(user=self.unassigned_worker, role="worker")
        self.site = Site.objects.create(
            name="Demo Site",
            location="Kolkata",
            start_date=timezone.localdate(),
            company_name="Demo Builders",
            created_by=self.manager,
        )
        self.site.workers.add(self.worker)

    def test_assigned_worker_can_check_in_once_with_active_qr(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse("generate_attendance_qr", args=[self.site.pk]))
        self.assertEqual(response.status_code, 302)
        attendance_qr = AttendanceQRCode.objects.get(site=self.site)

        self.client.force_login(self.worker)
        url = reverse("qr_check_in", args=[attendance_qr.token])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertTrue(Attendance.objects.filter(worker=self.worker, worksite=self.site).exists())
        self.client.post(url)
        self.assertEqual(Attendance.objects.filter(worker=self.worker, worksite=self.site).count(), 1)

    def test_unassigned_worker_and_expired_qr_are_rejected(self):
        attendance_qr = AttendanceQRCode.objects.create(
            site=self.site,
            created_by=self.manager,
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        url = reverse("qr_check_in", args=[attendance_qr.token])
        self.client.force_login(self.unassigned_worker)
        self.assertEqual(self.client.get(url).status_code, 403)

        attendance_qr.expires_at = timezone.now() - timedelta(minutes=1)
        attendance_qr.save()
        self.client.force_login(self.worker)
        self.assertEqual(self.client.get(url).status_code, 410)

class AuthorizationTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager_test",
            password="test-password",
        )
        UserProfile.objects.create(user=self.manager, role="manager")

        self.worker = User.objects.create_user(
            username="worker_test",
            password="test-password",
        )
        UserProfile.objects.create(user=self.worker, role="worker")

        self.superuser = User.objects.create_superuser(
            username="admin_test",
            password="test-password",
        )

        self.assigned_site = Site.objects.create(
            name="Assigned Site",
            location="Kolkata",
            start_date=timezone.localdate(),
            company_name="Demo Builders",
            created_by=self.manager,
        )
        self.assigned_site.workers.add(self.worker)

        self.other_site = Site.objects.create(
            name="Other Site",
            location="Howrah",
            start_date=timezone.localdate(),
            company_name="Demo Builders",
            created_by=self.manager,
        )

    def test_manager_can_open_manager_dashboard(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_open_manager_dashboard(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_worker_cannot_open_manager_add_site_page(self):
        self.client.force_login(self.worker)
        response = self.client.get(reverse("add_site"))
        self.assertEqual(response.status_code, 403)

    def test_worker_can_open_assigned_site_only(self):
        self.client.force_login(self.worker)

        assigned_response = self.client.get(
            reverse("worker_site_detail", args=[self.assigned_site.pk])
        )
        self.assertEqual(assigned_response.status_code, 200)

        unassigned_response = self.client.get(
            reverse("worker_site_detail", args=[self.other_site.pk])
        )
        self.assertEqual(unassigned_response.status_code, 404)