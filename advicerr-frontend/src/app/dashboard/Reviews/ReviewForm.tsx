import {
    Box,
    Heading,
    FormControl,
    FormLabel,
    Select,
    Textarea,
    Button,
    VStack,
    useToast,
  } from "@chakra-ui/react";
  import { useState } from "react";
  import { StarIcon } from "@chakra-ui/icons";
  import { useCreateReviewMutation } from "@/app/store/apis/reviewsApi";

  import usePrefixedTranslation from "@/app/hooks/usePrefixedTranslation";
  
  type Props = {
    reviewedUserId: string,
    firstName: string,
    lastName: string,
    consultantId: string
  }

  const ReviewForm = ({reviewedUserId, firstName, lastName, consultantId}: Props) => {
    const { t } = usePrefixedTranslation("Components.ReviewForm")
    
    const toast = useToast();
    const [selectedUser, setSelectedUser] = useState("");
    const [rating, setRating] = useState(0);
    const [description, setDescription] = useState("");

    const [createReview, { isLoading }] = useCreateReviewMutation();
  
    const handleSubmit = async () => {
        if (!selectedUser || rating === 0 || !description.trim()) {
          toast({
            title: t("errorToastLabel"),
            description: t("allFieldsErrorDescription"),
            status: "error",
            duration: 3000,
            isClosable: true,
          });
          return;
        }
    
        const newReview = {
          consultant_id: consultantId,
          client_id: reviewedUserId,
          rating,
          description,
        };
    
        try {
          await createReview(newReview).unwrap(); // Send review to backend
          toast({
            title: t("successToastLabel"),
            description: t("successDescription"),
            status: "success",
            duration: 3000,
            isClosable: true,
          });
    
          // Clear form
          setSelectedUser("");
          setRating(0);
          setDescription("");
        } catch (error) {
          console.error("Failed to submit review:", error);
          toast({
            title: t("errorToastLabel"),
            description: t("errorFailDescription"),
            status: "error",
            duration: 3000,
            isClosable: true,
          });
        }
      };
  
    return (
      <Box p={6} borderWidth="1px" borderRadius="lg" boxShadow="lg">
        <Heading as="h3" size="lg" mb={4}>
          {t("addReviewLabel")}
        </Heading>
        <VStack spacing={4}>
          {/* User Selection Dropdown */}
          <FormControl isRequired>
            <FormLabel>{t("selectUserLabel")}</FormLabel>
            <Select
              placeholder={t("placeholderLabel")}
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
            >
              {/* {users.map((user) => (
                <option key={user.consultant_id} value={user.consultant_id}>
                  {user.consultant.first_name} {user.consultant.last_name}
                </option>
              ))} */}
                <option >
                  {firstName} {lastName} 
                </option>
            </Select>
          </FormControl>
  
          {/* Star Rating */}
          <FormControl isRequired>
            <FormLabel>{t("ratingLabel")}</FormLabel>
            <Box display="flex">
              {[1, 2, 3, 4, 5].map((star) => (
                <StarIcon
                  key={star}
                  boxSize={6}
                  cursor="pointer"
                  color={star <= rating ? "yellow.400" : "gray.300"}
                  onClick={() => setRating(star)}
                />
              ))}
            </Box>
          </FormControl>
  
          {/* Review Description */}
          <FormControl isRequired>
            <FormLabel>{t("reviewLabel")}</FormLabel>
            <Textarea
              placeholder={t("reviewPlaceholder")}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </FormControl>
  
          {/* Submit Button */}
          <Button colorScheme="teal" size="lg" width="full" onClick={handleSubmit}>
            {t("submitLabel")}
          </Button>
        </VStack>
      </Box>
    );
  };
  
  export default ReviewForm;
  