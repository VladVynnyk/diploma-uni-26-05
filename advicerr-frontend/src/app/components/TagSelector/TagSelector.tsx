import { useState } from "react";
import {
  FormControl,
  FormLabel,
  HStack,
  Input,
  Button,
  IconButton,
  Select,
  Text
} from "@chakra-ui/react";
import { DeleteIcon } from "@chakra-ui/icons";
import { useGetTagsQuery } from "@/app/store/apis/tagsApi";
import usePrefixedTranslation from "@/app/hooks/usePrefixedTranslation";

import { TTagForUpdate } from "@/app/types/TagTypes";


type Props = {
  tags: Array<TTagForUpdate>,
  setTags: React.Dispatch<React.SetStateAction<TTagForUpdate[]>>
}

const MAX_TAGS = 3; // 🔥 Restrict to 3 tags

const TagSelector = ({ tags, setTags }: Props) => {
  const { t } = usePrefixedTranslation("Components.TagSelector")

  const { data: availableTags, isLoading } = useGetTagsQuery(); // Fetch tags
  const [customTag, setCustomTag] = useState(""); // For custom input
  const [selectedTag, setSelectedTag] = useState(""); // For dropdown

  // ✅ Handle selecting tag from dropdown
  const handleSelectTag = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const tagName = event.target.value;
    if (!tagName || tags.length >= MAX_TAGS) return; // Prevent empty selection or exceeding limit

    const existingTag = availableTags?.find((tag) => tag.name === tagName);
    if (!tags.some((tag) => tag.name === tagName)) {
      setTags([...tags, { name: tagName, description: existingTag?.description || "" }]);
    }
    setSelectedTag(""); // Reset dropdown
  };

  // ✅ Handle adding a custom tag
  const handleAddCustomTag = () => {
    if (customTag.trim() && !tags.some((tag) => tag.name === customTag) && tags.length < MAX_TAGS) {
      setTags([...tags, { name: customTag, description: "" }]);
      setCustomTag(""); // Reset input
    }
  };

  // ✅ Handle removing a tag
  const handleDeleteTag = (index: number) => {
    setTags(tags.filter((_, i) => i !== index));
  };

  return (
    <FormControl>
      <FormLabel>Tags</FormLabel>

      {/* Dropdown to select available tags */}
      <Select placeholder={t("dropdownPlaceholder")} onChange={handleSelectTag} value={selectedTag} isDisabled={isLoading || tags.length >= MAX_TAGS}>
        {availableTags?.map((tag) => (
          <option key={tag.id} value={tag.name}>
            {tag.name}
          </option>
        ))}
      </Select>

      {/* Input for custom tags */}
      <HStack mt={2}>
        <Input
          placeholder={t("inputPlaceholder")}
          value={customTag}
          onChange={(e) => setCustomTag(e.target.value)}
          flex="1"
          isDisabled={tags.length >= MAX_TAGS} // Disable input when max tags reached
        />
        <Button size="sm" onClick={handleAddCustomTag} colorScheme="blue" isDisabled={tags.length >= MAX_TAGS}>
          {t("inputButtonLabel")}
        </Button>
      </HStack>

      {/* 🔥 Show an alert if the user has reached the max tags */}
      {tags.length >= MAX_TAGS && <Text color="red.500" fontSize="sm">{t("errorMessageFirstPart")} {MAX_TAGS}{t("errorMessageSecondPart")}</Text>}

      {/* Display selected tags */}
      {tags.length > 0 && (
        <HStack wrap="wrap" spacing={2} mt={2}>
          {tags.map((tag, index) => (
            <HStack key={index} spacing={2}>
              <Input value={tag.name} isReadOnly flex="1" />
              <IconButton
                aria-label="Delete tag"
                icon={<DeleteIcon />}
                colorScheme="red"
                size="sm"
                onClick={() => handleDeleteTag(index)}
              />
            </HStack>
          ))}
        </HStack>
      )}
    </FormControl>
  );
};


export default TagSelector;
