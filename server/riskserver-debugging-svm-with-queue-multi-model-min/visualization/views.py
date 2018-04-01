from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.
from django.shortcuts import render
from django.views.generic import View

from query.models import Score
from riskserver import data_source
from trainapp.models import User, UploadedFile
from visualization.models import TestResult, ClusterResult


class Visualization(View):
    def update_test_result(self):
        # update TestResult

        # get all user pairs
        scores = Score.objects.all()
        user_pairs = []
        for score in scores:
            user_pair = (score.test_user, score.target_user)
            if user_pair not in user_pairs:
                user_pairs.append(user_pair)

        # analysis
        for user_pair in user_pairs:
            test_user = user_pair[0]
            target_user = user_pair[1]
            scores = Score.objects.filter(test_user=test_user, target_user=target_user).all()

            # analysis
            if test_user.imei[:15] == target_user.imei:
                self_verification = True
            else:
                self_verification = False

            total = len(scores)

            valid_scores = []
            for score in scores:
                if float(score.accuracy) >= 0.7:
                    valid_scores.append(score)
            valid = len(valid_scores)

            ratio = float(valid) / float(total)

            try:
                test_result = TestResult.objects.get(test_user=test_user, target_user=target_user)
                test_result.self_verification = self_verification
                test_result.acceptance_accuracy = 0.7
                test_result.valid = valid
                test_result.total = total
                test_result.ratio = ratio
                test_result.save()
            except ObjectDoesNotExist:
                TestResult.objects.create(test_user=test_user, target_user=target_user,
                                          self_verification=self_verification, acceptance_accuracy=0.7,
                                          valid=valid, total=total, ratio=ratio)

    def update_cluster_result(self):
        # update ClusterResult

        # clear all
        ClusterResult.objects.all().delete()

        # get all users
        users = User.objects.all()
        for user in users:
            # [{'target_model_box_order': 2, 'count': 34}, ]
            order_count_map = UploadedFile.objects.filter(
                user=user, is_lie=False, type='train', state='sit', is_dispatched=True,
                group_id__lte=data_source.LABEL_BEGIN
            ).values('target_model_box_order').annotate(count=Count('target_model_box_order'))
            if len(order_count_map) == 0:
                continue

            order_count_map = sorted(order_count_map, key=lambda element: element['target_model_box_order'])
            ClusterResult.objects.create(user=user, label_begin=data_source.LABEL_BEGIN,
                                         state='sit', model_number=len(order_count_map),
                                         description='/'.join([str(i['count']) for i in order_count_map]))

    def get(self, request, type):
        if type == 'test_result':
            self.update_test_result()
            return HttpResponseRedirect('/admin/visualization/testresult/')
        if type == 'cluster_result':
            self.update_cluster_result()
            return HttpResponseRedirect('/admin/visualization/clusterresult/')


    def post(self, request):
        return HttpResponse('Not implemented yet')
