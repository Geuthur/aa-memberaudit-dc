// React
import React from "react";

// Third Party
import { Filter, Search } from "lucide-react";
import {
  Button,
  Card,
  Col,
  Form,
  InputGroup,
  Row,
} from "react-bootstrap";
import { useTranslation } from "react-i18next";

export interface CorporationFilterBarProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  selectedCategory: string;
  onCategoryChange: (value: string) => void;
  categories: string[];
}

export const CorporationFilterBar: React.FC<CorporationFilterBarProps> = ({
  searchTerm,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  categories,
}) => {
  const { t } = useTranslation();

  return (
    <Card className="mb-4 aa-panel shadow-sm">
      <Card.Body className="p-3">
        <Row className="g-3 align-items-center">
          {/* Search */}
          <Col xs={12} md={6}>
            <InputGroup size="sm">
              <InputGroup.Text>
                <Search size={14} />
              </InputGroup.Text>
              <Form.Control
                type="text"
                placeholder={t("Filter by character or alt name...")}
                value={searchTerm}
                onChange={(e) => onSearchChange(e.target.value)}
              />
              {searchTerm && (
                <Button
                  variant="secondary"
                  className="aa-btn aa-btn-sm aa-btn-secondary"
                  onClick={() => onSearchChange("")}
                >
                  {t("Clear")}
                </Button>
              )}
            </InputGroup>
          </Col>

          {/* Category filter */}
          <Col xs={12} md={6}>
            <InputGroup size="sm">
              <InputGroup.Text>
                <Filter size={14} />
              </InputGroup.Text>
              <Form.Select
                value={selectedCategory}
                onChange={(e) => onCategoryChange(e.target.value)}
              >
                <option value="ALL">{t("All Categories")}</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </Form.Select>
            </InputGroup>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
};

export default CorporationFilterBar;
