import React, { useState } from 'react';

const OnboardingFlow = () => {
  // State to track current step and user data
  const [step, setStep] = useState(1);
  const [userData, setUserData] = useState({
    name: '',
    email: '',
    cookingApproach: '',
    storageSize: '',
    householdSize: ''
  });
  const [isComplete, setIsComplete] = useState(false);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setUserData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle radio/select option changes
  const handleOptionSelect = (field, value) => {
    setUserData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (step < 5) {
      setStep(prev => prev + 1);
    } else {
      setIsComplete(true);
    }
  };

  // Go back to previous step
  const handleBack = () => {
    if (step > 1) {
      setStep(prev => prev - 1);
    }
  };

  // Check if current step is valid to proceed
  const isStepValid = () => {
    switch (step) {
      case 1:
        return userData.name.trim() !== '';
      case 2:
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(userData.email);
      case 3:
        return userData.householdSize !== '';
      case 4:
        return userData.cookingApproach !== '';
      case 5:
        return userData.storageSize !== '';
      default:
        return false;
    }
  };

  // Cooking approach options
  const cookingApproachOptions = [
    { value: 'batch', label: 'Batch Cooking', icon: '🍲' },
    { value: 'daily', label: 'Cooking Daily', icon: '🍳' },
    { value: 'takeaway', label: 'Takeaways', icon: '🥡' },
    { value: 'ready', label: 'Ready Meals', icon: '🍱' }
  ];
  
  // Household size options
  const householdSizeOptions = [
    { value: '1', label: 'Just me', icon: '👤' },
    { value: '2', label: 'Two people', icon: '👥' },
    { value: '3-4', label: 'Small family (3-4)', icon: '👨‍👩‍👧' },
    { value: '5+', label: 'Large family (5+)', icon: '👨‍👩‍👧‍👧' }
  ];

  // Storage size options
  const storageSizeOptions = [
    { value: 'small', label: 'Small (Apartment-sized refrigerator)', icon: '🧊' },
    { value: 'medium', label: 'Medium (Standard refrigerator)', icon: '❄️' },
    { value: 'large', label: 'Large (Full-sized refrigerator with extra space)', icon: '🧊❄️' },
    { value: 'unlimited', label: 'Unlimited (Multiple or commercial-grade refrigeration)', icon: '🧊❄️🧊' }
  ];

  // Render different steps based on current state
  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="p-6 bg-white rounded-lg shadow-md max-w-md w-full">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center">
                <span className="text-3xl">🍽️</span>
              </div>
            </div>
            <div className="flex justify-between mt-6">
              <button
                onClick={handleBack}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={!isStepValid()}
                className={`px-4 py-2 rounded-md ${isStepValid() ? 'bg-yellow-500 text-white hover:bg-yellow-600' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
              >
                Next
              </button>
            </div>
            <h2 className="text-xl font-bold mb-6 text-center">Welcome! Let's get started</h2>
            <div className="mb-4">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                What should we call you?
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={userData.name}
                onChange={handleChange}
                placeholder="Your name"
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div className="flex justify-end mt-6">
              <button
                onClick={handleSubmit}
                disabled={!isStepValid()}
                className={`px-4 py-2 rounded-md ${isStepValid() ? 'bg-yellow-500 text-white hover:bg-yellow-600' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
              >
                Next
              </button>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="p-6 bg-white rounded-lg shadow-md max-w-md w-full">
            <h2 className="text-xl font-bold mb-6 text-center">Contact Information</h2>
            <div className="mb-4">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Your email address
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={userData.email}
                onChange={handleChange}
                placeholder="email@example.com"
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              <p className="mt-1 text-xs text-gray-500">We'll send your meal plans to this address</p>
            </div>
            <div className="flex justify-between mt-6">
              <button
                onClick={handleBack}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={!isStepValid()}
                className={`px-4 py-2 rounded-md ${isStepValid() ? 'bg-blue-500 text-white hover:bg-blue-600' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
              >
                Next
              </button>
            </div>
          </div>
        );
      case 3:
        return (
          <div className="p-6 bg-white rounded-lg shadow-md max-w-md w-full">
            <h2 className="text-xl font-bold mb-6 text-center">Your Household</h2>
            <div className="mb-4">
              <p className="block text-sm font-medium text-gray-700 mb-3">
                How many people are you cooking for?
              </p>
              <div className="grid grid-cols-2 gap-3">
                {householdSizeOptions.map((option) => (
                  <div
                    key={option.value}
                    className={`p-3 border rounded-md cursor-pointer text-center ${userData.householdSize === option.value ? 'border-yellow-500 bg-yellow-50' : 'border-gray-300 hover:bg-gray-50'}`}
                    onClick={() => handleOptionSelect('householdSize', option.value)}
                  >
                    <div className="text-3xl mb-2">{option.icon}</div>
                    <label className="cursor-pointer">
                      <input
                        type="radio"
                        name="householdSize"
                        value={option.value}
                        checked={userData.householdSize === option.value}
                        onChange={() => {}}
                        className="sr-only"
                      />
                      {option.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex justify-between mt-6">
              <button
                onClick={handleBack}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={!isStepValid()}
                className={`px-4 py-2 rounded-md ${isStepValid() ? 'bg-yellow-500 text-white hover:bg-yellow-600' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
              >
                Next
              </button>
            </div>
          </div>
        );
      case 4:
        return (
          <div className="p-6 bg-white rounded-lg shadow-md max-w-md w-full">
            <h2 className="text-xl font-bold mb-6 text-center">Your Cooking Approach</h2>
            <div className="mb-4">
              <p className="block text-sm font-medium text-gray-700 mb-3">
                What's your main approach to cooking?
              </p>
              <div className="grid grid-cols-2 gap-3">
                {cookingApproachOptions.map((option) => (
                  <div
                    key={option.value}
                    className={`p-3 border rounded-md cursor-pointer text-center ${userData.cookingApproach === option.value ? 'border-yellow-500 bg-yellow-50' : 'border-gray-300 hover:bg-gray-50'}`}
                    onClick={() => handleOptionSelect('cookingApproach', option.value)}
                  >
                    <div className="text-3xl mb-2">{option.icon}</div>
                    <label className="cursor-pointer">
                      <input
                        type="radio"
                        name="cookingApproach"
                        value={option.value}
                        checked={userData.cookingApproach === option.value}
                        onChange={() => {}}
                        className="sr-only"
                      />
                      {option.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex justify-between mt-6">
              <button
                onClick={handleBack}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={!isStepValid()}
                className={`px-4 py-2 rounded-md ${isStepValid() ? 'bg-blue-500 text-white hover:bg-blue-600' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
              >
                Next
              </button>
            </div>
          </div>
        );
      case 5:
        return (
          <div className="p-6 bg-white rounded-lg shadow-md max-w-md w-full">
            <h2 className="text-xl font-bold mb-6 text-center">Your Kitchen Setup</h2>
            <div className="mb-4">
              <p className="block text-sm font-medium text-gray-700 mb-3">
                What's your refrigerator/freezer size?
              </p>
              <div className="space-y-2">
                {storageSizeOptions.map((option) => (
                  <div
                    key={option.value}
                    className={`p-3 border rounded-md cursor-pointer ${userData.storageSize === option.value ? 'border-yellow-500 bg-yellow-50' : 'border-gray-300 hover:bg-gray-50'}`}
                    onClick={() => handleOptionSelect('storageSize', option.value)}
                  >
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="radio"
                        name="storageSize"
                        value={option.value}
                        checked={userData.storageSize === option.value}
                        onChange={() => {}}
                        className="sr-only"
                      />
                      <span className={`w-4 h-4 mr-2 rounded-full border ${userData.storageSize === option.value ? 'border-yellow-500 bg-yellow-500' : 'border-gray-400'}`}>
                        {userData.storageSize === option.value && (
                          <span className="block w-2 h-2 mx-auto mt-1 bg-white rounded-full" />
                        )}
                      </span>
                      {option.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex justify-between mt-6">
              <button
                onClick={handleBack}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={!isStepValid()}
                className={`px-4 py-2 rounded-md ${isStepValid() ? 'bg-blue-500 text-white hover:bg-blue-600' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
              >
                Complete Setup
              </button>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  // Render completion screen
  const renderCompletion = () => {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md max-w-md w-full text-center">
        <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold mb-2">You're all set, {userData.name}!</h2>
        <p className="text-gray-600 mb-6">
          We've created your profile based on your preferences. You're ready to start using our app!
        </p>
        <div className="bg-yellow-50 p-4 rounded-md mb-6 text-left border border-yellow-100">
          <h3 className="font-medium text-gray-700 mb-2">Your profile summary:</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-center"><span className="font-medium mr-2">Name:</span> {userData.name}</li>
            <li className="flex items-center"><span className="font-medium mr-2">Email:</span> {userData.email}</li>
            <li className="flex items-center">
              <span className="font-medium mr-2">Household:</span> 
              <span className="mr-1">
                {householdSizeOptions.find(o => o.value === userData.householdSize)?.icon}
              </span>
              {householdSizeOptions.find(o => o.value === userData.householdSize)?.label}
            </li>
            <li className="flex items-center">
              <span className="font-medium mr-2">Cooking approach:</span>
              <span className="mr-1">
                {cookingApproachOptions.find(o => o.value === userData.cookingApproach)?.icon}
              </span>
              {cookingApproachOptions.find(o => o.value === userData.cookingApproach)?.label}
            </li>
            <li className="flex items-center">
              <span className="font-medium mr-2">Storage size:</span> 
              {storageSizeOptions.find(o => o.value === userData.storageSize)?.label}
            </li>
          </ul>
        </div>
        <button
          className="w-full px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600"
        >
          Get Started
        </button>
      </div>
    );
  };

  // Progress bar calculation
  const progressPercentage = (step / 5) * 100;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4"
         style={{
           backgroundImage: `url("data:image/svg+xml,%3Csvg width='52' height='26' viewBox='0 0 52 26' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffbb00' fill-opacity='0.15'%3E%3Cpath d='M10 10c0-2.21-1.79-4-4-4-3.314 0-6-2.686-6-6h2c0 2.21 1.79 4 4 4 3.314 0 6 2.686 6 6 0 2.21 1.79 4 4 4 3.314 0 6 2.686 6 6 0 2.21 1.79 4 4 4v2c-3.314 0-6-2.686-6-6 0-2.21-1.79-4-4-4-3.314 0-6-2.686-6-6zm25.464-1.95l8.486 8.486-1.414 1.414-8.486-8.486 1.414-1.414z' /%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
           backgroundColor: '#fffbf0'
         }}>
      {!isComplete ? (
        <>
          <div className="w-full max-w-md mb-6">
            <div className="bg-gray-200 h-2 rounded-full">
              <div 
                className="bg-yellow-500 h-2 rounded-full transition-all duration-300 ease-in-out"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span className={step >= 1 ? "text-blue-500 font-medium" : ""}>Profile</span>
              <span className={step >= 2 ? "text-blue-500 font-medium" : ""}>Contact</span>
              <span className={step >= 3 ? "text-blue-500 font-medium" : ""}>Cooking</span>
              <span className={step >= 4 ? "text-blue-500 font-medium" : ""}>Kitchen</span>
            </div>
          </div>
          {renderStep()}
        </>
      ) : (
        renderCompletion()
      )}
    </div>
  );
};

export default OnboardingFlow;
