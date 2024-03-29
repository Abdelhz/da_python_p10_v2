"""
This module contains the view sets for the Issue and Comment models.

The IssuesViewSet includes an 'assign' action for assigning an issue to a user, and custom permission logic.
The CommentsViewSet includes custom permission logic.
"""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
#from projects.models import Project, Contributor
from users.models import CustomUser
from .models import Issue, Comment
from .serializers import IssueSerializer, CommentSerializer
from .permissions import IsIssueAuthor, IsIssueContributor, IsCommentAuthor, IsCommentContributor

class IssuesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the Issue model.

    This ViewSet allows issues to be viewed, created, updated, or deleted.
    It includes an 'assign' action for assigning an issue to a user, and custom permission logic.
    """
    serializer_class = IssueSerializer

    def get_queryset(self):
        """
        Return the queryset of issues for the specified project ID.
        """
        return Issue.objects.filter(project_id=self.kwargs['project_pk'])

    def create(self, request, *args, **kwargs):
        """
        Set project and issue_author automatically.
        :param request: The request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The result of the super().create() call.
        """
        request.data['project'] = self.kwargs['project_pk']
        request.data['issue_author'] = request.user.id
        request.data.setdefault('assignee', request.user.id)
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assigns the given issue to a user based on the user_id provided in the request data.
        Parameters:
            self: the object instance
            request: the request object
            pk: primary key of the issue (default=None)
        Returns:
            Response object with a status message.
        """
        issue = self.get_object()  # get the issue
        user_id = request.data.get('user_id')  # get the user_id from the request data

        # check if the user is a contributor to the project
        if not issue.project.contributor_set.filter(id=user_id).exists():
            # set the assignee back to the issue_author if the user does not exist or is not a contributor
            issue.assignee = issue.issue_author
            issue.save()
            return Response({'error': 'User is not a contributor to the project'}, status=status.HTTP_400_BAD_REQUEST)

        # get the user
        user = CustomUser.objects.get(id=user_id)

        # assign the issue to the user
        issue.assignee = user
        issue.save()

        return Response({'status': 'issue assigned'})
    def get_permissions(self):
        """
        This function returns a list of permission classes based on the action.
        It takes no parameters and returns a list of permission instances.
        """
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated, IsIssueContributor]
        elif self.action in ['update', 'partial_update', 'destroy', 'assign']:
            permission_classes = [permissions.IsAuthenticated, IsIssueAuthor]
        else:
            permission_classes = [permissions.IsAuthenticated, IsIssueContributor]
        return [permission() for permission in permission_classes]


class CommentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the Comment model.

    This ViewSet allows comments to be viewed, created, updated, or deleted.
    It includes custom permission logic.
    """
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        Returns a queryset of Comment objects filtered by the issue_id from the self.kwargs.
        """
        return Comment.objects.filter(issue_id=self.kwargs['issue_pk'])

    def create(self, request, *args, **kwargs):
        """
        Set comment_author and issue automatically.
        :param request: The request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The result of the super().create() call.
        """
        request.data['comment_author'] = request.user.id
        request.data['issue'] = self.kwargs['issue_pk']
        return super().create(request, *args, **kwargs)

    def get_permissions(self):
        """
        Retrieve the permissions required for the specified action.
        :return: List of permission classes required for the action
        :return type: list
        """
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated, IsCommentContributor]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsCommentAuthor]
        else:
            permission_classes = [permissions.IsAuthenticated, IsCommentContributor]
        return [permission() for permission in permission_classes]
