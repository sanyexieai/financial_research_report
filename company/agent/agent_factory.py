from enum import Enum

from app.new_agent.outline.outline_generator import OutlineGenerator
from app.new_agent.outline.outline_opinion_generator import OutlineOpinionGenerator
from .base_agent import BaseOutlineAgent
from company.agent.outline.outline_generator_part import OutlineGeneratorPart
from company.agent.outline.outline_opinion_generator_part import OutlineOpinionGeneratorPart
from app.new_agent.parts.part_abstract_generator import PartAbstractGenerator
from company.agent.parts.part_abstract_generator_part import PartAbstractGeneratorPart
from app.new_agent.parts.part_generator import PartGenerator
from company.agent.parts.part_generator_part import PartGeneratorPart
from app.new_agent.parts.part_opinion_generator import PartOpinionGenerator
from company.agent.parts.part_opinion_generator_part import PartOpinionGeneratorPart


class OutlineAgentType(Enum):
    """大纲 Agent 类型枚举"""
    OUTLINE_GENERATOR = "outline_generator"
    OUTLINE_OPINION_GENERATOR = "outline_opinion_generator"
    PART_GENERATOR = "part_generator"
    PART_OPINION_GENERATOR = "part_opinion_generator"
    PART_ABSTRACT_GENERATOR = "part_abstract_generator"

    OUTLINE_GENERATOR_PART = "outline_generator_part"
    OUTLINE_OPINION_GENERATOR_PART = "outline_opinion_generator_part"
    PART_GENERATOR_PART = "part_generator_part"
    PART_OPINION_GENERATOR_PART = "part_opinion_generator_part"
    PART_ABSTRACT_GENERATOR_PART = "part_abstract_generator_part"

class OutlineAgentFactory:
    """大纲 Agent 工厂类"""
    
    @staticmethod
    def create_agent(agent_type: OutlineAgentType, logger, llm) -> BaseOutlineAgent:
        """创建指定类型的 Agent"""
        if agent_type == OutlineAgentType.OUTLINE_GENERATOR:
            return OutlineGenerator(logger, llm)
        elif agent_type == OutlineAgentType.OUTLINE_OPINION_GENERATOR:
            return OutlineOpinionGenerator(logger, llm)
        elif agent_type == OutlineAgentType.PART_GENERATOR:
            return PartGenerator(logger, llm)
        elif agent_type == OutlineAgentType.PART_OPINION_GENERATOR:
            return PartOpinionGenerator(logger, llm)
        elif agent_type == OutlineAgentType.PART_ABSTRACT_GENERATOR:
            return PartAbstractGenerator(logger, llm)

        elif agent_type == OutlineAgentType.OUTLINE_GENERATOR_PART:
            return OutlineGeneratorPart(logger, llm)
        elif agent_type == OutlineAgentType.OUTLINE_OPINION_GENERATOR_PART:
            return OutlineOpinionGeneratorPart(logger, llm)
        elif agent_type == OutlineAgentType.PART_GENERATOR_PART:
            return PartGeneratorPart(logger, llm)
        elif agent_type == OutlineAgentType.PART_OPINION_GENERATOR_PART:
            return PartOpinionGeneratorPart(logger, llm)
        elif agent_type == OutlineAgentType.PART_ABSTRACT_GENERATOR_PART:
            return PartAbstractGeneratorPart(logger, llm)


        else:
            raise ValueError(f"不支持的 Agent 类型: {agent_type}")