from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Workspace
from .serializers import WorkspaceSerializer, WorkspaceCreateUpdateSerializer


class WorkspaceCreateAPIView(APIView):
    """
    Create workspace for logged-in user.
    Only one workspace is allowed per user in MVP.
    """

    def post(self, request):
        if hasattr(request.user, "workspace"):
            return Response(
                {
                    "status": "error",
                    "message": "Workspace already exists for this user."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = WorkspaceCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            workspace = serializer.save(owner=request.user)
            return Response(
                {
                    "status": "success",
                    "message": "Workspace created successfully.",
                    "data": WorkspaceSerializer(workspace).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class WorkspaceDetailAPIView(APIView):
    """
    Get logged-in user's workspace.
    """

    def get(self, request):
        try:
            workspace = request.user.workspace
        except Workspace.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "status": "success",
                "data": WorkspaceSerializer(workspace).data,
            },
            status=status.HTTP_200_OK
        )


class WorkspaceUpdateAPIView(APIView):
    """
    Update logged-in user's workspace.
    """

    def put(self, request):
        try:
            workspace = request.user.workspace
        except Workspace.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WorkspaceCreateUpdateSerializer(workspace, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Workspace updated successfully.",
                    "data": WorkspaceSerializer(workspace).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request):
        try:
            workspace = request.user.workspace
        except Workspace.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WorkspaceCreateUpdateSerializer(workspace, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Workspace updated successfully.",
                    "data": WorkspaceSerializer(workspace).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )