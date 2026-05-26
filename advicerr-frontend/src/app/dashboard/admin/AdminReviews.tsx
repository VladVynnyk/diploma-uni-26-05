"use client"
import React from 'react';
import { Box, Button, Heading, SimpleGrid, Text, useToast } from '@chakra-ui/react';
import StatusState from '@/app/components/StatusState/StatusState';
import { useDeleteAdminReviewMutation, useGetAdminReviewsQuery } from '@/app/store/apis/reviewsApi';

type Props = {
  token: string,
}

const AdminReviews = ({ token }: Props) => {
  const toast = useToast();
  const { data, error, isLoading, refetch } = useGetAdminReviewsQuery(token);
  const [deleteAdminReview, { isLoading: isDeleting }] = useDeleteAdminReviewMutation();

  const handleDeleteReview = async (reviewId: string) => {
    try {
      await deleteAdminReview({ token, reviewId }).unwrap();
      toast({
        title: "Відгук видалено",
        description: "Некоректний відгук успішно видалено.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      refetch();
    } catch (deleteError: any) {
      toast({
        title: "Не вдалося видалити відгук",
        description: String(deleteError?.data?.detail || "Спробуйте ще раз."),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  if (isLoading) {
    return <StatusState message="Завантаження відгуків..." variant="loading" size="section" />;
  }

  if (error) {
    return <StatusState message="Не вдалося завантажити відгуки." variant="error" size="section" />;
  }

  return (
    <Box>
      <Heading as="h2" size="xl" mb={4}>
        Усі відгуки
      </Heading>
      <SimpleGrid columns={{ base: 1, xl: 2 }} spacing={4}>
        {data?.map((review) => (
          <Box key={review.id} borderWidth="1px" borderRadius="lg" p={4}>
            <Text fontWeight="bold">Оцінка: {review.rating}/5</Text>
            <Text color="gray.600">Клієнт: {review.client?.first_name} {review.client?.last_name}</Text>
            <Text color="gray.600">Консультант ID: {review.consultant_id}</Text>
            <Text mt={2} mb={4}>{review.description || "Без тексту"}</Text>
            <Button
              colorScheme="red"
              size="sm"
              isLoading={isDeleting}
              onClick={() => handleDeleteReview(review.id)}
            >
              Видалити відгук
            </Button>
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default AdminReviews;
