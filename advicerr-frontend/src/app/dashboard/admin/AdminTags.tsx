"use client"
import React from 'react';
import { Box, Button, FormControl, FormLabel, Heading, Input, SimpleGrid, Text, Textarea, useToast, VStack } from '@chakra-ui/react';
import StatusState from '@/app/components/StatusState/StatusState';
import { useCreateTagMutation, useDeleteTagMutation, useGetTagsQuery, useUpdateTagMutation } from '@/app/store/apis/tagsApi';

type Props = {
  token: string,
}

const AdminTags = ({ token }: Props) => {
  const toast = useToast();
  const { data, error, isLoading, refetch } = useGetTagsQuery();
  const [createTag, { isLoading: isCreating }] = useCreateTagMutation();
  const [updateTag, { isLoading: isUpdating }] = useUpdateTagMutation();
  const [deleteTag, { isLoading: isDeleting }] = useDeleteTagMutation();

  const [newTagName, setNewTagName] = React.useState("");
  const [newTagDescription, setNewTagDescription] = React.useState("");
  const [editingTagId, setEditingTagId] = React.useState<string | null>(null);
  const [editingTagName, setEditingTagName] = React.useState("");
  const [editingTagDescription, setEditingTagDescription] = React.useState("");

  const handleCreateTag = async () => {
    if (!newTagName.trim()) {
      toast({
        title: "Не вдалося створити тег",
        description: "Вкажіть назву тегу.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      await createTag({
        token,
        body: {
          name: newTagName.trim(),
          description: newTagDescription.trim(),
        }
      }).unwrap();
      setNewTagName("");
      setNewTagDescription("");
      toast({
        title: "Тег створено",
        description: "Новий тег успішно додано.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      refetch();
    } catch (createError: any) {
      toast({
        title: "Не вдалося створити тег",
        description: String(createError?.data?.detail || "Спробуйте ще раз."),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const startEdit = (tag: { id: string; name: string; description: string }) => {
    setEditingTagId(tag.id);
    setEditingTagName(tag.name);
    setEditingTagDescription(tag.description || "");
  };

  const handleUpdateTag = async () => {
    if (!editingTagId || !editingTagName.trim()) {
      return;
    }

    try {
      await updateTag({
        token,
        id: editingTagId,
        body: {
          name: editingTagName.trim(),
          description: editingTagDescription.trim(),
        }
      }).unwrap();
      setEditingTagId(null);
      setEditingTagName("");
      setEditingTagDescription("");
      toast({
        title: "Тег оновлено",
        description: "Тег успішно змінено.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      refetch();
    } catch (updateError: any) {
      toast({
        title: "Не вдалося оновити тег",
        description: String(updateError?.data?.detail || "Спробуйте ще раз."),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleDeleteTag = async (id: string) => {
    try {
      await deleteTag({ token, id }).unwrap();
      toast({
        title: "Тег видалено",
        description: "Тег успішно видалено.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      refetch();
    } catch (deleteError: any) {
      toast({
        title: "Не вдалося видалити тег",
        description: String(deleteError?.data?.detail || "Спробуйте ще раз."),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  if (isLoading) {
    return <StatusState message="Завантаження тегів..." variant="loading" size="section" />;
  }

  if (error) {
    return <StatusState message="Не вдалося завантажити теги." variant="error" size="section" />;
  }

  return (
    <Box>
      <Heading as="h2" size="xl" mb={4}>
        Усі теги
      </Heading>

      <Box borderWidth="1px" borderRadius="lg" p={4} mb={6}>
        <VStack spacing={3} align="stretch">
          <FormControl isRequired>
            <FormLabel>Назва нового тегу</FormLabel>
            <Input value={newTagName} onChange={(e) => setNewTagName(e.target.value)} />
          </FormControl>
          <FormControl>
            <FormLabel>Опис нового тегу</FormLabel>
            <Textarea value={newTagDescription} onChange={(e) => setNewTagDescription(e.target.value)} />
          </FormControl>
          <Button colorScheme="teal" onClick={handleCreateTag} isLoading={isCreating}>
            Створити тег
          </Button>
        </VStack>
      </Box>

      <SimpleGrid columns={{ base: 1, md: 2, xl: 3 }} spacing={4}>
        {data?.map((tag) => (
          <Box key={tag.id} borderWidth="1px" borderRadius="lg" p={4}>
            {editingTagId === tag.id ? (
              <VStack spacing={3} align="stretch">
                <Input value={editingTagName} onChange={(e) => setEditingTagName(e.target.value)} />
                <Textarea value={editingTagDescription} onChange={(e) => setEditingTagDescription(e.target.value)} />
                <Button colorScheme="blue" onClick={handleUpdateTag} isLoading={isUpdating}>
                  Зберегти зміни
                </Button>
                <Button variant="ghost" onClick={() => setEditingTagId(null)}>
                  Скасувати
                </Button>
              </VStack>
            ) : (
              <VStack spacing={3} align="stretch">
                <Text fontWeight="bold">{tag.name}</Text>
                <Text color="gray.600">{tag.description || "Без опису"}</Text>
                <Button size="sm" colorScheme="blue" onClick={() => startEdit(tag)}>
                  Редагувати
                </Button>
                <Button size="sm" colorScheme="red" isLoading={isDeleting} onClick={() => handleDeleteTag(tag.id)}>
                  Видалити
                </Button>
              </VStack>
            )}
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default AdminTags;
