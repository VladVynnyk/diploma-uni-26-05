"use client"
import React, { MouseEventHandler } from 'react'
import { Box, Text, Button, VStack, HStack, Avatar, Tag, Select } from "@chakra-ui/react";
import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';
import ReviewForm from '../Reviews/ReviewForm';
import { Order } from '@/app/types/OrderTypes';

type Props = {
  orderId: string,
  typeOfOrder: "incoming" | "outcoming",
  clientId: string,
  consultantId: string,
  name: string,
  surname: string,
  price: number,
  status: Order["status"],
  topic: string,
  message: string,
  scheduledAt: string | null,
  durationMinutes: number,
  clientEmail?: string,
  clientPhoneNumber?: string,
  canChangeStatus?: boolean,
  availableStatuses?: Array<Order["status"]>,
  isUpdatingStatus?: boolean,
  onChat: MouseEventHandler<HTMLButtonElement | undefined>,
  onStatusChange?: (nextStatus: Order["status"]) => void
}

const STATUS_LABELS: Record<Order["status"], string> = {
  new: "Нова",
  confirmed: "Підтверджено",
  in_progress: "В процесі",
  completed: "Завершено",
  cancelled: "Скасовано",
};

const SingleOrder = ({
  clientId,
  consultantId,
  name,
  surname,
  price,
  typeOfOrder,
  status,
  topic,
  message,
  scheduledAt,
  durationMinutes,
  clientEmail,
  clientPhoneNumber,
  canChangeStatus = false,
  availableStatuses = [],
  isUpdatingStatus = false,
  onStatusChange,
}: Props) => {
  const { t } = usePrefixedTranslation('Components.SingleOrder');

  const [isReviewFormOpen, setIsReviewFormOpen] = React.useState(false);

  const onAddReview = () => {
    setIsReviewFormOpen((prev) => !prev);
  };

  return (
    <Box
      bg="white"
      boxShadow="md"
      borderRadius="md"
      p={4}
      border="1px solid"
      borderColor="gray.200"
      w="full"
      _hover={{ boxShadow: "lg" }}
    >
      <HStack spacing={4} align="start">
        <Avatar name={name} />
        <VStack align="start" spacing={1} flex="1">
          <Text>
            {typeOfOrder === 'outcoming' ? t("youOrderedLabel") : ""}
          </Text>
          <Text fontSize="lg">
            {name} {surname}
          </Text>
          <Tag colorScheme={typeOfOrder === 'incoming' ? 'green' : 'gray'}>
            {typeOfOrder === 'incoming' ? t("incomingOrderLabel") : t("outcomingOrderLabel")}
          </Tag>
          <Text color="gray.500">
            {typeOfOrder === 'incoming' ? t("someoneOrderedLabel") : ""}
          </Text>
          <Text color="gray.500">
            {t("priceLabel")}: {price}
          </Text>
          <Text color="gray.500">
            Тема: {topic}
          </Text>
          {message ? (
            <Text color="gray.500">
              Деталі: {message}
            </Text>
          ) : null}
          <Text color="gray.500">
            Коли: {scheduledAt ? new Date(scheduledAt).toLocaleString() : "Погоджується окремо"}
          </Text>
          <Text color="gray.500">
            Тривалість: {durationMinutes} хв
          </Text>
          {typeOfOrder === "incoming" && (clientEmail || clientPhoneNumber) ? (
            <>
              <Text color="gray.500">
                Ел-пошта: {clientEmail || "Не вказано"}
              </Text>
              <Text color="gray.500">
                Телефон: {clientPhoneNumber || "Не вказано"}
              </Text>
            </>
          ) : null}
        </VStack>
        <VStack spacing={2} align="stretch">
          {canChangeStatus && onStatusChange ? (
            <Select
              size="sm"
              value={status}
              onChange={(e) => onStatusChange(e.target.value as Order["status"])}
              isDisabled={isUpdatingStatus}
            >
              {availableStatuses.map((value) => (
                <option key={value} value={value}>
                  {STATUS_LABELS[value]}
                </option>
              ))}
            </Select>
          ) : (
            <Tag colorScheme="blue">{STATUS_LABELS[status]}</Tag>
          )}
          <Button colorScheme="blue" size="sm" onClick={onAddReview}>
            {t("reviewButtonLabel")}
          </Button>
        </VStack>
      </HStack>
      {isReviewFormOpen && (
        <ReviewForm
          reviewedUserId={clientId}
          consultantId={consultantId}
          firstName={name}
          lastName={surname}
        />
      )}
    </Box>
  )
}

export default SingleOrder
