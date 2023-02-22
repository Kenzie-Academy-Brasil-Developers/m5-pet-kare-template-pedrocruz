from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView, Request, Response, status
from groups.models import Group
from pets.models import Pet
from rest_framework.pagination import PageNumberPagination
from pets.models import Pet
from django.shortcuts import get_object_or_404
from pets.serializers import PetSerializer
from traits.models import Trait


class PetsView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        traits = request.query_params.get("trait", None)
        pets = Pet.objects.all()
        if traits:

            traits_filter = Pet.objects.filter(traits__name=traits).all()
            result_page = self.paginate_queryset(traits_filter, request, view=self)
            serializer = PetSerializer(result_page, many=True)

            return self.get_paginated_response(serializer.data)

        result_page = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop("group")
        traits_list = serializer.validated_data.pop("traits")
        group = Group.objects.filter(
            scientific_name__iexact=group_data["scientific_name"]
        ).first()

        if not group:
            group = Group.objects.create(**group_data)

        pet_obj = Pet.objects.create(**serializer.validated_data, group=group)

        for trait_dict in traits_list:
            trait_obj = Trait.objects.filter(name__iexact=trait_dict["name"]).first()

            if not trait_obj:
                trait_obj = Trait.objects.create(**trait_dict)
                pet_obj.traits.add(trait_obj)

            pet_obj.traits.add(trait_obj)

        serializer = PetSerializer(pet_obj)

        return Response(serializer.data, status.HTTP_201_CREATED)


class PetsDetailView(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id = pet_id)
        serializer = PetSerializer(pet)

        return Response(serializer.data)

    def patch(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id = pet_id)

        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop("group", None)
        traits_data: list = serializer.validated_data.pop("traits", None)

        if group_data:

            group_obj = Group.objects.filter(
                scientific_name__iexact=group_data["scientific_name"]
            ).first()

            if not group_obj:
                group_obj = Group.objects.create(**group_data)

            pet.group = group_obj

        if traits_data:
            trait_list = []
            for trait_dict in traits_data:

                trait_obj = Trait.objects.filter(
                    name__iexact=trait_dict["name"]
                ).first()

                if not trait_obj:
                    trait_obj = Trait.objects.create(**trait_dict)

                trait_list.append(trait_obj)

            pet.traits.set(trait_list)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()
        serializer = PetSerializer(pet)

        return Response(serializer.data)

    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)

        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

