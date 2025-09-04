import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ProcedurePage from './ProcedurePage';

const ProcedureViewPage = () => {
  const { procedureId } = useParams();
  const navigate = useNavigate();

  const handleBackToHome = () => {
    navigate('/procedure-library');
  };

  const handleBackToSpecialty = () => {
    navigate('/procedure-library');
  };

  return (
    <ProcedurePage
      procedureId={procedureId}
      onBackToHome={handleBackToHome}
      onBackToSpecialty={handleBackToSpecialty}
    />
  );
};

export default ProcedureViewPage;