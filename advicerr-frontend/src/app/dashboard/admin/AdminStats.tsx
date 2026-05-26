"use client"
import React from 'react';
import { Box, Heading, SimpleGrid, Stat, StatLabel, StatNumber } from '@chakra-ui/react';
import StatusState from '@/app/components/StatusState/StatusState';
import { useGetAdminStatsQuery } from '@/app/store/apis/usersApi';

type Props = {
  token: string,
}

const AdminStats = ({ token }: Props) => {
  const { data, error, isLoading } = useGetAdminStatsQuery(token);

  if (isLoading) {
    return <StatusState message="Завантаження статистики..." variant="loading" size="section" />;
  }

  if (error || !data) {
    return <StatusState message="Не вдалося завантажити статистику." variant="error" size="section" />;
  }

  const stats = [
    ["Усього користувачів", data.total_users],
    ["Консультантів", data.total_consultants],
    ["Клієнтів", data.total_clients],
    ["Усього консультацій", data.total_orders],
    ["Нові", data.new_orders],
    ["Підтверджені", data.confirmed_orders],
    ["В роботі", data.in_progress_orders],
    ["Завершені", data.completed_orders],
    ["Скасовані", data.cancelled_orders],
    ["Усього відгуків", data.total_reviews],
    ["Середній рейтинг", data.average_rating.toFixed(1)],
    ["Усього тегів", data.total_tags],
  ];

  return (
    <Box>
      <Heading as="h2" size="xl" mb={4}>
        Статистика системи
      </Heading>
      <SimpleGrid columns={{ base: 1, md: 2, xl: 3 }} spacing={4}>
        {stats.map(([label, value]) => (
          <Stat key={label} borderWidth="1px" borderRadius="lg" p={4}>
            <StatLabel>{label}</StatLabel>
            <StatNumber>{value}</StatNumber>
          </Stat>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default AdminStats;
