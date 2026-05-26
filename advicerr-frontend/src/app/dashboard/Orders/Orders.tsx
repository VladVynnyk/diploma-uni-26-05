import React from 'react'
import { Heading, SimpleGrid, useToast } from '@chakra-ui/react';
import Cookies from 'js-cookie';
import SingleOrder from './SingleOrder'
import StatusState from '@/app/components/StatusState/StatusState';

import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation'

import { useGetAllOrdersQuery, useUpdateOrderStatusMutation } from '@/app/store/apis/ordersApi';
import { ORDER_STATUS_TRANSITIONS, Order } from '@/app/types/OrderTypes';
import { TMeUser } from '@/app/types/UserTypes';

type Props = {
  currentUser: TMeUser
}

const Orders = ({ currentUser }: Props) => {
  const { t } = usePrefixedTranslation('Pages.DashboardPage.orders');
  const loadingLabel = "Завантаження консультацій...";
  const errorLoadingLabel = "Не вдалося завантажити консультації.";
  const emptyLabel = "Запитів на консультації ще немає.";
  const token = Cookies.get("access_token") || "";
  const toast = useToast();
  const { data, error, isLoading, refetch } = useGetAllOrdersQuery({ id: currentUser.id, token })
  const [updateOrderStatus, { isLoading: isUpdatingStatus }] = useUpdateOrderStatusMutation();

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

  const getAvailableStatuses = (currentStatus: Order["status"]) => {
    return [currentStatus, ...ORDER_STATUS_TRANSITIONS[currentStatus]];
  };

  if (isLoading) {
    return <StatusState message={loadingLabel} variant="loading" size="section" />;
  }

  if (error) {
    return <StatusState message={errorLoadingLabel} variant="error" size="section" />;
  }

  return (
    <div>
      <Heading as="h2" size="xl" mb={4}>
        {t("ordersLabel")}
      </Heading>

      {!data?.length && (
        <StatusState message={emptyLabel} variant="empty" size="section" />
      )}

      <SimpleGrid columns={{ base: 1, xl: 2 }} spacing={4}>
        {data?.map((order) => {
          const orderType = currentUser.id === order.consultant_id ? "incoming" : "outcoming";
          const user = orderType === "incoming" ? order.client : order.consultant;

          return (
            <SingleOrder
              key={order.id}
              orderId={order.id}
              clientId={order.client?.id || order.client_id}
              consultantId={order.consultant?.id || order.consultant_id}
              typeOfOrder={orderType}
              name={user.first_name}
              surname={user.last_name}
              price={order.price}
              status={order.status}
              topic={order.topic}
              message={order.message}
              scheduledAt={order.scheduled_at}
              durationMinutes={order.duration_minutes}
              clientEmail={order.client?.email}
              clientPhoneNumber={order.client?.phone_number}
              canChangeStatus={order.consultant_id === currentUser.id}
              availableStatuses={getAvailableStatuses(order.status)}
              isUpdatingStatus={isUpdatingStatus}
              onStatusChange={(nextStatus) => handleStatusChange(order.id, nextStatus)}
              onChat={() => console.log(`Chat with ${user.first_name}`)}
            />
          );
        })}
      </SimpleGrid>
    </div>
  )
}

export default Orders
