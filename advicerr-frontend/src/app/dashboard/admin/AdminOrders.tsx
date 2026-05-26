"use client"
import React from 'react';
import { Box, Heading, Select, SimpleGrid, Text, useToast } from '@chakra-ui/react';
import StatusState from '@/app/components/StatusState/StatusState';
import { useGetAdminOrdersQuery, useUpdateOrderStatusMutation } from '@/app/store/apis/ordersApi';
import { ORDER_STATUS_TRANSITIONS, Order } from '@/app/types/OrderTypes';

type Props = {
  token: string,
}

const STATUS_LABELS: Record<Order["status"], string> = {
  new: "Новий",
  confirmed: "Підтверджено",
  in_progress: "В роботі",
  completed: "Завершено",
  cancelled: "Скасовано",
};

const AdminOrders = ({ token }: Props) => {
  const toast = useToast();
  const { data, error, isLoading, refetch } = useGetAdminOrdersQuery(token);
  const [updateOrderStatus, { isLoading: isUpdating }] = useUpdateOrderStatusMutation();

  const getAvailableStatuses = (currentStatus: Order["status"]) => {
    return [currentStatus, ...ORDER_STATUS_TRANSITIONS[currentStatus]];
  };

  const handleStatusChange = async (orderId: string, status: Order["status"]) => {
    try {
      await updateOrderStatus({ token, orderId, body: { status } }).unwrap();
      toast({
        title: "Статус оновлено",
        description: "Стан консультації успішно змінено.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      refetch();
    } catch (updateError: any) {
      toast({
        title: "Не вдалося оновити статус",
        description: String(updateError?.data?.detail || "Спробуйте ще раз."),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  if (isLoading) {
    return <StatusState message="Завантаження консультацій..." variant="loading" size="section" />;
  }

  if (error) {
    return <StatusState message="Не вдалося завантажити консультації." variant="error" size="section" />;
  }

  return (
    <Box>
      <Heading as="h2" size="xl" mb={4}>
        Усі консультації
      </Heading>
      <SimpleGrid columns={{ base: 1, xl: 2 }} spacing={4}>
        {data?.map((order) => (
          <Box key={order.id} borderWidth="1px" borderRadius="lg" p={4}>
            <Heading as="h3" size="md" mb={2}>{order.topic}</Heading>
            <Text color="gray.600">Клієнт: {order.client?.first_name} {order.client?.last_name}</Text>
            <Text color="gray.600">Email клієнта: {order.client?.email || "Не вказано"}</Text>
            <Text color="gray.600">Телефон клієнта: {order.client?.phone_number || "Не вказано"}</Text>
            <Text color="gray.600">Консультант: {order.consultant?.first_name} {order.consultant?.last_name}</Text>
            <Text color="gray.600">Ціна: {order.price}</Text>
            <Text color="gray.600">Коли: {order.scheduled_at ? new Date(order.scheduled_at).toLocaleString() : "Погоджується окремо"}</Text>
            <Text color="gray.600">Тривалість: {order.duration_minutes} хв</Text>
            <Text color="gray.600" mb={3}>Повідомлення: {order.message || "Не вказано"}</Text>
            <Select
              value={order.status}
              onChange={(e) => handleStatusChange(order.id, e.target.value as Order["status"])}
              isDisabled={isUpdating}
            >
              {getAvailableStatuses(order.status).map((value) => (
                <option key={value} value={value}>{STATUS_LABELS[value]}</option>
              ))}
            </Select>
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default AdminOrders;
