import usePrefixedTranslation from "../hooks/usePrefixedTranslation";

//set functions - it's state functions from useState
export const validateEmail = (email: string, setEmailError: (error: string | null) => void, t: (key: string) => string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email.trim()) {
      // setEmailError("Email is required.");
      setEmailError(t("emailIsRequiredInputError"));
      return false;
    } else if (!emailRegex.test(email)) {
      // setEmailError("Invalid email format.");
      setEmailError(t("emailInvalidInputError"));
      return false;
    } else {
      setEmailError(null);
      return true;
    }
  };
  
//set functions - it's state functions from useState
  export const validatePhoneNumber = (phoneNumber: string, setPhoneNumberError: (error: string | null) => void, t: (key: string) => string): boolean => {
    const phoneRegex = /^[0-9]{10,15}$/;  // Allows only digits, with length 10-15
    if (!phoneNumber.trim()) {
      // setPhoneNumberError("Phone number is required.");
      setPhoneNumberError(t("phoneIsRequiredInputError"));
      return false;
    } else if (!phoneRegex.test(phoneNumber)) {
      // setPhoneNumberError("Invalid phone number format. Use 10-15 digits.");
      setPhoneNumberError(t("phoneInvalidInputError"));
      return false;
    } else {
      setPhoneNumberError(null);
      return true;
    }
  };
  