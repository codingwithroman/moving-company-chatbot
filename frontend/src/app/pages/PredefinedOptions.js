import React from 'react';

const PredefinedOptions = ({ actionProvider }) => {
const options = [
    {
    text: "Annuleringsbeleid",
    handler: () => actionProvider.handleMessage("Wat is het annuleringsbeleid?"),
    id: 1
    },
    {
    text: "Verhuisvoorwaarden",
    handler: () => actionProvider.handleMessage("Wat zijn de belangrijkste verhuisvoorwaarden?"),
    id: 2
    },
    {
    text: "Tarieven",
    handler: () => actionProvider.handleMessage("Wat zijn jullie tarieven voor verhuizing?"),
    id: 3
    },
    {
    text: "Contact",
    handler: () => actionProvider.handleMessage("Hoe kan ik contact met jullie opnemen?"),
    id: 4
    }
];

return (
    <div className="options-container">
    {options.map((option) => (
        <button
        key={option.id}
        onClick={option.handler}
        className="option-button"
        >
        {option.text}
        </button>
    ))}
    </div>
);
};

export default PredefinedOptions;