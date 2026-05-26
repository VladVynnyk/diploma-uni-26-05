"use client"
import React from 'react';
import { Badge, Box, Flex, Heading, SimpleGrid, Switch, Text, useToast } from '@chakra-ui/react';
import StatusState from '@/app/components/StatusState/StatusState';
import { useGetAdminUsersQuery, useUpdateAdminStatusMutation } from '@/app/store/apis/usersApi';

type Props = {
  token: string,
  currentUserId: string,
}

const AdminUsers = ({ token, currentUserId }: Props) => {
  const toast = useToast();
  const { data, error, isLoading, refetch } = useGetAdminUsersQuery(token);
  const [updateAdminStatus, { isLoading: isUpdating }] = useUpdateAdminStatusMutation();

  const handleToggle = async (userId: string, currentValue: boolean) => {
    try {
      await updateAdminStatus({ token, userId, is_admin: !currentValue }).unwrap();
      toast({
        title: "Права доступу оновлено",
        description: "Роль адміністратора успішно змінено.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      refetch();
    } catch (toggleError: any) {
      toast({
        title: "Не вдалося змінити роль",
        description: String(toggleError?.data?.detail || "Спробуйте ще раз."),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  if (isLoading) {
    return <StatusState message="Завантаження користувачів..." variant="loading" size="section" />;
  }

  if (error) {
    return <StatusState message="Не вдалося завантажити користувачів." variant="error" size="section" />;
  }

  return (
    <Box>
      <Heading as="h2" size="xl" mb={4}>
        Усі користувачі
      </Heading>
      <SimpleGrid columns={{ base: 1, xl: 2 }} spacing={4}>
        {data?.map((user) => (
          <Box key={user.id} borderWidth="1px" borderRadius="lg" p={4}>
            <Flex justify="space-between" align="center" mb={2}>
              <Text fontWeight="bold">{user.first_name} {user.last_name}</Text>
              <Badge colorScheme={user.is_consultant ? "green" : "gray"}>
                {user.is_consultant ? "Консультант" : "Клієнт"}
              </Badge>
            </Flex>
            <Text color="gray.600">{user.email}</Text>
            <Text color="gray.600">Телефон: {user.phone_number || "Не вказано"}</Text>
            <Text color="gray.600">Вартість: {user.price ?? 0}</Text>
            <Flex justify="space-between" align="center" mt={4}>
              <Text>Адміністратор</Text>
              <Switch
                isChecked={user.is_admin}
                isDisabled={isUpdating || (currentUserId === user.id && user.is_admin)}
                onChange={() => handleToggle(user.id, user.is_admin)}
              />
            </Flex>
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default AdminUsers;
