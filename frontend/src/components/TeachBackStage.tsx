import React from 'react';

interface CourseConcept {
  title: string;
  difficulty_level: 'beginner' | 'medium' | 'advanced';
  status: 'not_started' | 'reviewing' | 'reviewed' | 'not_interested' | 'already_know';
  type: 'original' | 'related';
}

interface TeachBackStageProps {
  concepts: CourseConcept[];
}

function TeachBackStage({ concepts }: TeachBackStageProps) {
  return (
    <div className="space-y-6">
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-3xl">🎓</span>
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Teach Back Stage</h3>
        <p className="text-gray-600 max-w-md mx-auto">
          Demonstrate your understanding by explaining concepts back. Practice the Feynman Technique to solidify your learning.
        </p>
        <div className="mt-6 text-sm text-gray-500">
          Ready to teach: {concepts.filter(c => c.status === 'reviewed').length} concepts
        </div>
      </div>
    </div>
  );
}

export default TeachBackStage;
